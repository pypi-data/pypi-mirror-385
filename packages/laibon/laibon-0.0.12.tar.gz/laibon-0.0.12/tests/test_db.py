import unittest
import uuid
from unittest.mock import Mock
import os
import django
from django.conf import settings

# Configure Django settings for testing
if not settings.configured:
    settings.configure(
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
        ],
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        USE_TZ=True,
    )
    django.setup()

from laibon import db


class TestAdapter(db.Adapter):
    def __init__(self, entity_id=None, name=None):
        super().__init__(entity_id)
        self.name = name
    
    def to_model(self, existing=None):
        mock_model = Mock()
        mock_model.name = self.name
        return mock_model
    
    def get_model_class(self):
        return Mock


class TestDB(unittest.TestCase):
    
    def test_adapter_init_with_valid_uuid(self):
        test_id = str(uuid.uuid4())
        adapter = TestAdapter(test_id)
        self.assertEqual(adapter.get_id(), test_id)
    
    def test_adapter_init_with_invalid_uuid(self):
        with self.assertRaises(ValueError):
            TestAdapter("invalid-uuid")
    
    def test_adapter_from_model(self):
        mock_model = Mock()
        mock_model.id = uuid.uuid4()
        adapter = TestAdapter()
        adapter.from_model(mock_model)
        self.assertEqual(adapter.get_id(), str(mock_model.id))
    
    def test_adapter_to_model(self):
        adapter = TestAdapter(name="test")
        model = adapter.to_model()
        self.assertEqual(model.name, "test")


if __name__ == '__main__':
    unittest.main()
