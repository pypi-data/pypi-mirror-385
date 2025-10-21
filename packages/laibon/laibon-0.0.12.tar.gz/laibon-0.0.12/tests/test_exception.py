import unittest

from laibon import exception


class TestExceptions(unittest.TestCase):
    
    def test_base_exception_with_message(self):
        exc = exception.BaseException("test message")
        self.assertEqual(exc.get_message(), "test message")
        self.assertEqual(str(exc), "test message")
    
    def test_base_exception_with_cause(self):
        cause = ValueError("original error")
        exc = exception.BaseException("wrapper", cause)
        self.assertEqual(exc.cause, cause)
    
    def test_processing_exception_default_message(self):
        exc = exception.ProcessingException()
        self.assertEqual(exc.get_message(), "An unexpected error occured")
    
    def test_invalid_query_exception(self):
        exc = exception.InvalidQueryException("bad query")
        self.assertEqual(exc.get_message(), "bad query")
    
    def test_persistence_exception(self):
        exc = exception.PersistenceException("write failed")
        self.assertEqual(exc.get_message(), "write failed")
    
    def test_invalid_argument_exception(self):
        exc = exception.InvalidArgumentException("invalid arg")
        self.assertEqual(exc.message, "invalid arg")


if __name__ == '__main__':
    unittest.main()
