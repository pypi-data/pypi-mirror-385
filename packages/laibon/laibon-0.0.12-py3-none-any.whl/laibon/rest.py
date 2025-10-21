# Copyright Wenceslaus Mumala 2023. See LICENSE file.

import json
import logging
import os

import jsonschema
from django.core.cache import cache
from django.http import request as django_request

from laibon import common
from laibon import exception

logger = logging.getLogger(__name__)


class JSONValidationException(exception.BaseException):
    def __init__(self, msg="Validation for request against schema failed", cause=None):
        super().__init__(msg, cause)


RESOURCE_PATH = os.environ.get('RESOURCES_PATH', '/tmp')


class JSONSchemaValidator:
    """Thread-safe JSON schema validator with Django caching.
    
    Validates JSON input against schemas stored in the filesystem.
    Schemas are cached for performance and thread safety.
    
    Environment Variables:
        RESOURCES_PATH: Directory containing schema files (defaults to /tmp)
    
    Example:
        # Validate request data against schema
        try:
            JSONSchemaValidator.validate_schema(
                {"name": "John", "age": 30}, 
                "user/create_request.json"
            )
        except JSONValidationException as e:
            # Handle validation error
            pass
    """

    @staticmethod
    def _load_request_schema(schema_file):
        with open(schema_file, "r") as f:
            return json.load(f)

    @staticmethod
    def _get_schema(schema_path):
        """Load schema with Django caching"""
        cache_key = f"schema:{schema_path}"
        schema = cache.get(cache_key)
        
        if schema is None:
            try:
                schema = JSONSchemaValidator._load_request_schema(schema_path)
                cache.set(cache_key, schema, timeout=3600)  # Cache for 1 hour
            except Exception as e:
                raise JSONValidationException(f"Could not read schema file: {e}")
        
        return schema

    @staticmethod
    def validate_schema(input_json, json_schema):
        request_schema = os.path.join(RESOURCE_PATH, json_schema)
        schema_json = JSONSchemaValidator._get_schema(request_schema)

        try:
            jsonschema.validate(input_json, schema_json)
        except jsonschema.exceptions.ValidationError as e:
            logger.error("Error validating request: %s", str(e))
            raise JSONValidationException("Validation for request against schema failed.", e)


class RestRequest(common.FlowRequest):
    def __init__(self, http_request: django_request.HttpRequest, uri_params):
        super().__init__()
        if isinstance(http_request, django_request.HttpRequest) is False:
            raise exception.InvalidArgumentException()

        self._request = http_request
        self._uri_params = [] if uri_params is None else uri_params

    def get_request_body(self):
        return self._request.body if self._request else None

    def get_query_params(self) -> django_request.QueryDict:
        """Returns the query params e.g name in ?name=blah"""
        return self._request.GET if self._request else django_request.QueryDict()

    def get_uri_params(self):  # Users should take note of the order of occurrence
        """Returns the params configured in the URI in urls.py"""
        return self._uri_params

    def get_host(self):
        return self._request.get_host()

    def get_scheme(self):
        """ Whether request is http or https """
        return self._request.scheme

    def get_headers(self) -> django_request.HttpHeaders:
        return self._request.headers if self._request else None

    def get_header_value(self, header_key, default_value=None):
        headers = self.get_headers()
        return headers.get(header_key, default_value) if headers else default_value

    def get_session_data(self, session_key):
        return self._request.COOKIES.get(session_key) if self._request else None

    def get_query_parameter(self, key, def_value=None):
        return self.get_query_params().get(key, def_value)

    def get_session_id(self):
        return self.get_session_data('sessionid')

    def get_interface_http_request(self):
        """Should be used only for authentication purposes."""
        return self._request

    def validate(self):
        pass


class TrafficRequest(RestRequest):
    def __init__(self, http_request: django_request.HttpRequest, uri_params):
        super().__init__(http_request, uri_params)


class JsonRequest(TrafficRequest):
    """Request with json payload"""

    def __init__(self, http_request: django_request.HttpRequest, uri_params, parsed_json):
        super().__init__(http_request, uri_params)


class DataContainer(common.Container):
    """Container purposed for Rest requests"""
    FLOW_REQUEST_KEY = "FlowRequest"
    FLOW_EXCEPTION_KEY = "DelayedException"
    FLOW_RESPONSE = "FlowResponse"

    def __init__(self, http_request: django_request.HttpRequest, uri_params):
        super().__init__()
        self._request = http_request
        self._uri_params = [] if uri_params is None else uri_params

    def get_raw_request(self):
        """External django http request object"""
        return self._request

    def get_uri_params(self):
        """Uri params from external rest request"""
        return self._uri_params

    def get_or_raise(self, key):
        v = self.get(key)
        if v is None:
            raise exception.MissingContainerValueException()
        return v

    def get_request(self) -> common.FlowRequest:
        return self.get_or_raise(self.FLOW_REQUEST_KEY)

    def set_request(self, flow_request):
        if isinstance(flow_request, common.FlowRequest) is False:
            raise exception.InvalidArgumentException()

        existing = self.get(self.FLOW_REQUEST_KEY)
        if not existing:
            self.put(self.FLOW_REQUEST_KEY, flow_request)

    def set_exception(self, e):
        existing = self.get(self.FLOW_EXCEPTION_KEY)
        if not existing:
            self.put(self.FLOW_EXCEPTION_KEY, e)


CACHED_SCHEMA_LOCATIONS = {}


class ParseJsonRequestActivity(common.Activity):
    """Reads json request, parses it into expected request and sets result on container"""
    LOGGER = logging.getLogger(__name__)
    SCHEMA_HTTP_HEADER = "scheme"

    class ParsedJSON(common.JSONObject):
        def __init__(self, dict_):
            self.__dict__.update(dict_)

        @staticmethod
        def parseJSON(d):
            return json.loads(json.dumps(d), object_hook=ParseJsonRequestActivity.ParsedJSON)

    def __init__(self, request_class: type, schema_file: str = None):
        super().__init__()
        self._schema_file = schema_file
        self._request_class = request_class

    def get_schema_path(self, request: django_request.HttpRequest):
        # TODO
        headers = request.headers if request else None
        req_location: str = headers.get(ParseJsonRequestActivity.SCHEMA_HTTP_HEADER, None) if headers else None
        if not req_location:
            return None

        cached = CACHED_SCHEMA_LOCATIONS.get(req_location)
        if cached:
            return cached

        scheme = request.scheme
        host = request.get_host()
        host_part = scheme + "//" + host
        if req_location.startswith(host_part) is False:
            raise exception.InvalidArgumentException("Schema path is invalid")
        loc = req_location.partition(host_part)[2]
        if not loc:
            raise exception.InvalidArgumentException("Problem determining schema path")
        CACHED_SCHEMA_LOCATIONS[req_location] = loc
        return loc

    class Result(common.ActivityResult):
        VALIDATION_ERROR = "ValidationError"
        INVALID_REQUEST = "InvalidRequest"

    def get_result_codes(self):
        return [self.Result.VALIDATION_ERROR, self.Result.INVALID_REQUEST]

    def process(self, data_container: DataContainer):
        self.LOGGER.debug("Validating and parsing request.")
        original_request = data_container.get_raw_request()

        schema_loc = self._schema_file if self._schema_file else self.get_schema_path(original_request)
        parsed_json = None
        if schema_loc is not None:
            try:
                raw_body = original_request.body
                body = json.loads(raw_body)
                JSONSchemaValidator.validate_schema(body, schema_loc)
                parsed_json = self.ParsedJSON.parseJSON(body)
            except JSONValidationException as e:
                self.LOGGER.error("Error validating request.", exc_info=True)
                data_container.set_exception(e)
                return self.Result.VALIDATION_ERROR
            except Exception as e:
                self.LOGGER.error("Unexpected error while validating request.", exc_info=True)
                data_container.set_exception(e)
                return self.Result.VALIDATION_ERROR
        # Create request
        try:
            request_instance: JsonRequest = (
                self._request_class(original_request, data_container.get_uri_params(), parsed_json))
            data_container.set_request(request_instance)
            self.LOGGER.debug("Successfully parsed request.")
        except Exception as e:
            self.LOGGER.error("Error parsing external request: %s", str(e), exc_info=True)
            error = exception.ProcessingException(cause=e)
            data_container.set_exception(error)
            return self.Result.INVALID_REQUEST
        return common.goto_next()


class SetupContentFreeRequestActivity(common.Activity):
    """Prepares request for GET or DELETE operations"""
    LOGGER = logging.getLogger(__name__)

    def __init__(self, request_class: type, schema_file: str = None):
        super().__init__()
        self._schema_file = schema_file
        self._request_class = request_class

    class Result(common.ActivityResult):
        INVALID_REQUEST = "InvalidRequest"

    def get_result_codes(self):
        return [self.Result.INVALID_REQUEST]

    def process(self, data_container: DataContainer):
        self.LOGGER.debug("Validating and parsing request.")
        original_request = data_container.get_raw_request()
        try:
            request_instance: TrafficRequest = (self._request_class(original_request, data_container.get_uri_params()))
            request_instance.validate()
            data_container.set_request(request_instance)
            self.LOGGER.debug("Successfully parsed request.")
        except Exception as e:
            self.LOGGER.error("Error parsing external request: %s", str(e), exc_info=True)
            error = exception.ProcessingException(cause=e)
            data_container.set_exception(error)
            return self.Result.INVALID_REQUEST
        return common.goto_next()
