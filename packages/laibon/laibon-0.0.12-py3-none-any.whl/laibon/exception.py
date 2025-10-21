# Copyright Wenceslaus Mumala 2023. See LICENSE file.

class BaseException(Exception):
    def __init__(self, msg, cause=None):
        self.message = msg
        super().__init__(msg)
        self.cause = cause

    def get_message(self):
        return self.message


class ProcessingException(BaseException):
    def __init__(self, msg="An unexpected error occured", cause=None):
        super().__init__(msg, cause)


class InvalidQueryException(BaseException):
    def __init__(self, msg="Invalid query or missing parameters", cause=None):
        super().__init__(msg, cause)


class QueryExecutionException(BaseException):
    """If an error is returned while reading data from db"""

    def __init__(self, msg="Error executing query against database", cause=None):
        super().__init__(msg, cause)


class ResultsetProcessingException(BaseException):
    """If an error is returned while processing data that has been read from db"""

    def __init__(self, msg="Error while processing result set from query", cause=None):
        super().__init__(msg, cause)


class MissingContainerValueException(BaseException):
    def __init__(self, msg="Expected value is missing from container", cause=None):
        super().__init__(msg, cause)


class InvalidFlowDefinition(BaseException):
    def __init__(self, msg="Invalid jump location", cause=None):
        super().__init__(msg, cause)


class PersistenceException(BaseException):
    """If an error is returned while writing data"""

    def __init__(self, msg="Error writing data", cause=None):
        super().__init__(msg, cause)


class InvalidArgumentException(BaseException):
    def __init__(self, msg="Invalid argument provided", cause=None):
        super().__init__(msg, cause)
        self.message = msg  # Keep for backward compatibility
