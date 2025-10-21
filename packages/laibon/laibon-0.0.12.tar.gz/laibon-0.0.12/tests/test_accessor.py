import unittest

from laibon import accessor, common, exception


class TestAccessor(unittest.TestCase):
    
    def test_delayed_exception_accessor_set_get(self):
        container = common.Container()
        test_exception = Exception("test error")
        
        accessor.DelayedExceptionAccessor.set(test_exception, container)
        result = accessor.DelayedExceptionAccessor.get(container)
        
        self.assertEqual(result, test_exception)
    
    def test_delayed_exception_accessor_get_none(self):
        container = common.Container()
        result = accessor.DelayedExceptionAccessor.get(container)
        self.assertIsNone(result)
    
    def test_delayed_exception_accessor_set_none_raises(self):
        container = common.Container()
        with self.assertRaises(exception.InvalidArgumentException):
            accessor.DelayedExceptionAccessor.set(None, container)


if __name__ == '__main__':
    unittest.main()
