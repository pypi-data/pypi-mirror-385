import unittest
import json
import tempfile
import os
from unittest.mock import patch, call
import django
from django.conf import settings
from django.core.cache import cache

# Configure Django before importing rest module
os.environ.setdefault('RESOURCES_PATH', '/tmp')

if not settings.configured:
    settings.configure(
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            }
        },
        USE_TZ=True,
    )
    django.setup()

from laibon import rest


class TestCaching(unittest.TestCase):
    
    def setUp(self):
        cache.clear()
        self.temp_dir = tempfile.mkdtemp()
        self.schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        self.schema_file = os.path.join(self.temp_dir, "test_schema.json")
        with open(self.schema_file, 'w') as f:
            json.dump(self.schema, f)
    
    def tearDown(self):
        if os.path.exists(self.schema_file):
            os.remove(self.schema_file)
        os.rmdir(self.temp_dir)
        cache.clear()
    
    @patch.object(rest.JSONSchemaValidator, '_load_request_schema')
    def test_schema_caching(self, mock_load):
        mock_load.return_value = self.schema
        
        with patch.object(rest, 'RESOURCE_PATH', self.temp_dir):
            # First call should load from file
            rest.JSONSchemaValidator.validate_schema({"name": "test"}, "test_schema.json")
            self.assertEqual(mock_load.call_count, 1)
            
            # Second call should use cache
            rest.JSONSchemaValidator.validate_schema({"name": "test2"}, "test_schema.json")
            self.assertEqual(mock_load.call_count, 1)  # Still 1, not called again


if __name__ == '__main__':
    unittest.main()
