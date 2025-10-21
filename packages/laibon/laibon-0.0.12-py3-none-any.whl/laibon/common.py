# Copyright Wenceslaus Mumala 2023. See LICENSE file.

import datetime
import enum
import json
from abc import abstractmethod

from laibon import exception


class AbstractEnum(enum.Enum):
    """Base class for enums with value conversion capabilities."""
    
    def __init__(self, value):
        self._value = value

    def to_value(self):
        """Return the underlying value of this enum."""
        return self._value

    @classmethod
    def from_value(cls, val):
        """Create enum instance from value, returns None if not found."""
        for v in cls:
            if v.to_value() == val:
                return v
        return None


class ContainerKey:
    """Hashable key for Container storage with string-based equality."""
    
    def __init__(self, key):
        self.key = key

    def __eq__(self, other):
        return isinstance(other, ContainerKey) and self.key == other.key

    def __hash__(self):
        return hash(self.key)


class Container:
    """Generic key-value storage for passing data between activities.
    
    Used throughout flows to store and retrieve data. Accessors provide
    type-safe access patterns for specific data types.
    """

    def __init__(self):
        self._container = {}

    def get(self, key):
        """Retrieve value by key, returns None if not found."""
        return self._container.get(key)

    def put(self, key, value):
        """Store value with given key."""
        self._container[key] = value


class FlowRequest:
    pass


class ContainerDataAccessor:
    def __init__(self, key: ContainerKey):
        self._key = key

    def set(self, data, data_container: Container):
        if not isinstance(data, self.get_data_type()):
            raise exception.InvalidArgumentException()
        data_container.put(self._key, data)

    def get(self, data_container: Container):
        return data_container.get(self._key)

    def get_or_raise(self, data_container: Container):
        v = data_container.get(self._key)
        if v is None:
            raise exception.MissingContainerValueException()
        return v

    @abstractmethod
    def get_data_type(self) -> type:
        raise NotImplementedError


class ActivityResult(enum.Enum):
    def __init__(self, value):
        self._value = value

    def to_value(self):
        return self._value

    @classmethod
    def from_value(cls, val):
        for v in cls:
            if v.to_value() == val:
                return v
        return None


class DefaultActivityResult(ActivityResult):
    # Reserved result codes
    NEXT = "next"


def goto_next() -> ActivityResult:
    return DefaultActivityResult.NEXT


class Activity:
    """
    Sub classes must contain methods with a prededifined name and each must return a Result object.
    Result code 0 should mean completed ok and should proceed normally
    """

    def __init__(self):
        pass

    @abstractmethod
    def process(self, container: Container) -> ActivityResult:
        raise NotImplementedError

    def get_result_codes(self):
        raise NotImplementedError


class JSONObject(object):
    JSON_DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

    def date_to_json_format(self, dt):
        return dt.strftime(self.JSON_DATE_TIME_FORMAT)

    def default_parser(self, o):
        """
        Default public parser for json
        """
        if isinstance(o, datetime.datetime):
            return self.date_to_json_format(o)
        if isinstance(o, enum.Enum):
            return o.name
        return o.__dict__

    def get_parser(self):
        return self.default_parser

    def toJSON(self):
        return json.dumps(self, default=self.get_parser(), sort_keys=True, indent=4)


class ListData(JSONObject):
    def __init__(self):
        self._data = []

    def add(self, entry):
        if isinstance(entry, self.get_data_class()):
            self._data.append(entry)
        else:
            raise exception.InvalidArgumentException("Instance does not match expected class.")

    def is_empty(self):
        return self.get_size() == 0

    @abstractmethod
    def get_data_class(self) -> type:
        raise NotImplementedError

    def iterator(self):
        return iter(self._data)

    def get_item_at(self, index: int):
        return self._data[index]

    def get_first(self):
        return self.get_item_at(0)

    def get_size(self):
        return len(self._data)

    def sort_data(self, sorter_lamda):  # e.g. f = lambda h: h.name
        sort_list = list(self._data)
        sort_list.sort(key=sorter_lamda)
        return iter(sort_list)

    def map_to_list(self, map_function):
        list_data = list(self._data)
        return list(map(map_function, list_data))
