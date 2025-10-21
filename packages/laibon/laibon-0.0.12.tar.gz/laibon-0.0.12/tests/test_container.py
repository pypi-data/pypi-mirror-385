import unittest

from laibon import common


class TestContainer(unittest.TestCase):
    def test_get(self):
        container = common.Container()
        key = common.ContainerKey("key")
        data = "Hello"
        container.put(key, data)
        self.assertEqual(container.get(key), data)

    def test_get_missing_key(self):
        container = common.Container()
        key = common.ContainerKey("key")
        self.assertIsNone(container.get(key))

    def test_get_new_key(self):
        container = common.Container()
        key = common.ContainerKey("key")
        data = "Hello"
        container.put(key, data)
        key2 = common.ContainerKey("key")
        self.assertEqual(container.get(key2), data)


if __name__ == '__main__':
    unittest.main()
