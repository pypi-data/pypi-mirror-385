import unittest
import json
import tempfile
import os
from unittest.mock import patch
import django
from django.conf import settings

# Set environment variable and configure Django before importing rest module
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


class TestJSONValidation(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            },
            "required": ["name"]
        }
        
        self.schema_file = os.path.join(self.temp_dir, "test_schema.json")
        with open(self.schema_file, 'w') as f:
            json.dump(self.schema, f)
    
    def tearDown(self):
        if os.path.exists(self.schema_file):
            os.remove(self.schema_file)
        os.rmdir(self.temp_dir)
    
    @patch.dict(os.environ, {'RESOURCES_PATH': ''})
    def test_validate_schema_valid_input(self):
        with patch.object(rest, 'RESOURCE_PATH', self.temp_dir):
            input_data = {"name": "John", "age": 30}
            # Should not raise exception
            rest.JSONSchemaValidator.validate_schema(input_data, "test_schema.json")
    
    @patch.dict(os.environ, {'RESOURCES_PATH': ''})
    def test_validate_schema_invalid_input(self):
        with patch.object(rest, 'RESOURCE_PATH', self.temp_dir):
            input_data = {"age": 30}  # missing required 'name'
            with patch('laibon.rest.logger.error'):  # Mock the logger to avoid formatting issues
                with self.assertRaises(rest.JSONValidationException):
                    rest.JSONSchemaValidator.validate_schema(input_data, "test_schema.json")
    
    @patch.dict(os.environ, {'RESOURCES_PATH': ''})
    def test_validate_schema_missing_file(self):
        with patch.object(rest, 'RESOURCE_PATH', self.temp_dir):
            input_data = {"name": "John"}
            with self.assertRaises(rest.JSONValidationException):
                rest.JSONSchemaValidator.validate_schema(input_data, "nonexistent.json")


if __name__ == '__main__':
    unittest.main()
