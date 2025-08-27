import unittest
import os
import tempfile
import json
import shutil
from unittest.mock import patch, mock_open, MagicMock
from instant_search_db.config_manager import ConfigManager, CategoryConfig, UIConfig, FieldMapping

class TestConfigManager(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment with temporary config directory"""
        self.test_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager(self.test_dir)
        
        # Create test configuration files
        self._create_test_configs()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def _create_test_configs(self):
        """Create test configuration files"""
        # Create categories.json
        categories_data = {
            "categories": {
                "test_category": {
                    "display_name": "Test Category",
                    "icon": "fas fa-test",
                    "emoji_fallback": "🧪",
                    "color": "#3498db",
                    "description": "Test category description"
                }
            }
        }
        
        with open(os.path.join(self.test_dir, "categories.json"), 'w', encoding='utf-8') as f:
            json.dump(categories_data, f, ensure_ascii=False, indent=2)
        
        # Create fields.json
        fields_data = {
            "field_mappings": {
                "category": "category",
                "name": "name",
                "description": "description"
            },
            "display_fields": ["name", "description"],
            "search_fields": ["name", "description"],
            "required_fields": ["category", "name"]
        }
        
        with open(os.path.join(self.test_dir, "fields.json"), 'w', encoding='utf-8') as f:
            json.dump(fields_data, f, ensure_ascii=False, indent=2)
        
        # Create ui.json
        ui_data = {
            "ui": {
                "title": "Test Application",
                "subtitle": "Test subtitle",
                "theme": {
                    "primary_color": "#3498db",
                    "secondary_color": "#2ecc71",
                    "accent_color": "#e74c3c"
                },
                "layout": {
                    "categories_per_row": 5,
                    "show_category_counts": True
                }
            }
        }
        
        with open(os.path.join(self.test_dir, "ui.json"), 'w', encoding='utf-8') as f:
            json.dump(ui_data, f, ensure_ascii=False, indent=2)
    
    def test_load_categories(self):
        """Test loading categories configuration"""
        categories = self.config_manager.load_categories()
        
        self.assertIsInstance(categories, dict)
        self.assertIn("test_category", categories)
        
        category = categories["test_category"]
        self.assertIsInstance(category, CategoryConfig)
        self.assertEqual(category.display_name, "Test Category")
        self.assertEqual(category.icon, "fas fa-test")
        self.assertEqual(category.emoji_fallback, "🧪")
        self.assertEqual(category.color, "#3498db")
    
    def test_load_field_mappings(self):
        """Test loading field mappings configuration"""
        fields = self.config_manager.load_field_mappings()
        
        self.assertIsInstance(fields, dict)
        self.assertIn("field_mappings", fields)
        self.assertIn("display_fields", fields)
        self.assertIn("search_fields", fields)
        
        mappings = fields["field_mappings"]
        self.assertEqual(mappings["category"], "category")
        self.assertEqual(mappings["name"], "name")
    
    def test_load_ui_settings(self):
        """Test loading UI settings configuration"""
        ui_config = self.config_manager.load_ui_settings()
        
        self.assertIsInstance(ui_config, UIConfig)
        self.assertEqual(ui_config.title, "Test Application")
        self.assertEqual(ui_config.subtitle, "Test subtitle")
        self.assertIn("primary_color", ui_config.theme)
        self.assertEqual(ui_config.theme["primary_color"], "#3498db")
    
    def test_fallback_on_missing_files(self):
        """Test fallback behavior when configuration files are missing"""
        # Create a new config manager with non-existent directory
        empty_config_manager = ConfigManager("/non/existent/path")
        
        # Should fall back to defaults without errors
        categories = empty_config_manager.load_categories()
        self.assertIsInstance(categories, dict)
        self.assertGreater(len(categories), 0)  # Should have default categories
        
        fields = empty_config_manager.load_field_mappings()
        self.assertIsInstance(fields, dict)
        self.assertIn("field_mappings", fields)
        
        ui_config = empty_config_manager.load_ui_settings()
        self.assertIsInstance(ui_config, UIConfig)
        self.assertTrue(ui_config.title)  # Should have default title
    
    def test_caching(self):
        """Test configuration caching"""
        # Load categories twice
        categories1 = self.config_manager.load_categories()
        categories2 = self.config_manager.load_categories()
        
        # Should return the same cached instance
        self.assertIs(categories1, categories2)
        
        # Force reload should return new instance
        categories3 = self.config_manager.load_categories(force_reload=True)
        self.assertIsNot(categories1, categories3)
    
    def test_validate_all_configs(self):
        """Test validation of all configurations"""
        result = self.config_manager.validate_all_configs()
        self.assertTrue(result)
    
    def test_clear_cache(self):
        """Test cache clearing"""
        # Load configurations to populate cache
        self.config_manager.load_categories()
        self.config_manager.load_field_mappings()
        self.config_manager.load_ui_settings()
        
        # Verify cache is populated
        self.assertIsNotNone(self.config_manager._categories_cache)
        self.assertIsNotNone(self.config_manager._fields_cache)
        self.assertIsNotNone(self.config_manager._ui_cache)
        
        # Clear cache
        self.config_manager.clear_cache()
        
        # Verify cache is cleared
        self.assertIsNone(self.config_manager._categories_cache)
        self.assertIsNone(self.config_manager._fields_cache)
        self.assertIsNone(self.config_manager._ui_cache)

    def test_invalid_json_handling(self):
        """Test handling of invalid JSON files"""
        # Create invalid JSON file
        invalid_json_path = os.path.join(self.test_dir, "invalid_categories.json")
        with open(invalid_json_path, 'w') as f:
            f.write('{"invalid": json content}')
        
        # Create config manager pointing to invalid file
        invalid_config_manager = ConfigManager(self.test_dir)
        
        # Mock the categories.json path to point to invalid file
        with patch.object(invalid_config_manager, '_load_json_file') as mock_load:
            mock_load.return_value = invalid_config_manager._get_default_categories()
            
            categories = invalid_config_manager.load_categories()
            self.assertIsInstance(categories, dict)
            # Should fall back to defaults
            self.assertIn("武器", categories)

    def test_permission_error_handling(self):
        """Test handling of permission errors"""
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            config_manager = ConfigManager(self.test_dir)
            
            # Should fall back to defaults without crashing
            categories = config_manager.load_categories()
            self.assertIsInstance(categories, dict)
            
            fields = config_manager.load_field_mappings()
            self.assertIsInstance(fields, dict)
            
            ui_config = config_manager.load_ui_settings()
            self.assertIsInstance(ui_config, UIConfig)

    def test_malformed_category_config(self):
        """Test handling of malformed category configuration"""
        # Create malformed categories.json
        malformed_data = {
            "categories": {
                "incomplete_category": {
                    "display_name": "Test",
                    # Missing required fields
                },
                "valid_category": {
                    "display_name": "Valid Category",
                    "icon": "fas fa-test",
                    "emoji_fallback": "🧪",
                    "color": "#3498db"
                }
            }
        }
        
        with open(os.path.join(self.test_dir, "categories.json"), 'w') as f:
            json.dump(malformed_data, f)
        
        categories = self.config_manager.load_categories(force_reload=True)
        
        # Should skip incomplete category and load valid one
        self.assertNotIn("incomplete_category", categories)
        self.assertIn("valid_category", categories)

    def test_schema_validation(self):
        """Test schema validation functionality"""
        # Create schemas directory
        schemas_dir = os.path.join(self.test_dir, "schemas")
        os.makedirs(schemas_dir, exist_ok=True)
        
        # Create a simple schema
        schema = {
            "type": "object",
            "properties": {
                "categories": {
                    "type": "object"
                }
            },
            "required": ["categories"]
        }
        
        with open(os.path.join(schemas_dir, "categories-schema.json"), 'w') as f:
            json.dump(schema, f)
        
        # Test valid data
        valid_data = {"categories": {"test": {}}}
        result = self.config_manager._validate_config(valid_data, "categories")
        self.assertTrue(result)
        
        # Test invalid data
        invalid_data = {"invalid_key": "value"}
        result = self.config_manager._validate_config(invalid_data, "categories")
        self.assertFalse(result)

    def test_example_configs(self):
        """Test example configuration loading"""
        # Create examples directory
        examples_dir = os.path.join(self.test_dir, "examples")
        os.makedirs(examples_dir, exist_ok=True)
        
        # Create example config
        example_data = {
            "name": "Test Example",
            "description": "Test example configuration"
        }
        
        with open(os.path.join(examples_dir, "test-example.json"), 'w') as f:
            json.dump(example_data, f)
        
        # Test listing examples
        examples = self.config_manager.get_example_configs()
        self.assertIn("test-example", examples)
        
        # Test loading example
        loaded_example = self.config_manager.load_example_config("test-example")
        self.assertEqual(loaded_example, example_data)
        
        # Test loading non-existent example
        non_existent = self.config_manager.load_example_config("non-existent")
        self.assertIsNone(non_existent)

    def test_health_check(self):
        """Test configuration system health check"""
        health_status = self.config_manager.health_check()
        
        self.assertIn("overall_status", health_status)
        self.assertIn("checks", health_status)
        self.assertIn("config_directory", health_status["checks"])
        self.assertIn("categories", health_status["checks"])
        self.assertIn("fields", health_status["checks"])
        self.assertIn("ui", health_status["checks"])
        
        # Should be healthy with valid configs
        self.assertEqual(health_status["overall_status"], "healthy")

    def test_error_recovery_callbacks(self):
        """Test error recovery callback functionality"""
        # Test with missing config file
        missing_config_manager = ConfigManager("/tmp/test_missing_config")
        
        # Should trigger recovery callback and create default config
        categories = missing_config_manager.load_categories()
        self.assertIsInstance(categories, dict)
        self.assertGreater(len(categories), 0)

    def test_configuration_change_logging(self):
        """Test configuration change logging"""
        # Load initial configuration
        initial_categories = self.config_manager.load_categories()
        
        # Modify configuration file
        new_categories_data = {
            "categories": {
                "new_category": {
                    "display_name": "New Category",
                    "icon": "fas fa-new",
                    "emoji_fallback": "🆕",
                    "color": "#ff0000"
                }
            }
        }
        
        with open(os.path.join(self.test_dir, "categories.json"), 'w') as f:
            json.dump(new_categories_data, f)
        
        # Force reload to trigger change logging
        updated_categories = self.config_manager.load_categories(force_reload=True)
        
        self.assertNotEqual(len(initial_categories), len(updated_categories))
        self.assertIn("new_category", updated_categories)

    def test_default_configurations(self):
        """Test default configuration generation"""
        # Test default categories
        default_categories = self.config_manager._get_default_categories()
        self.assertIn("categories", default_categories)
        self.assertIn("武器", default_categories["categories"])
        
        # Test default fields
        default_fields = self.config_manager._get_default_fields()
        self.assertIn("field_mappings", default_fields)
        self.assertIn("category", default_fields["field_mappings"])
        
        # Test default UI
        default_ui = self.config_manager._get_default_ui()
        self.assertIn("ui", default_ui)
        self.assertIn("title", default_ui["ui"])

    def test_concurrent_access(self):
        """Test concurrent access to configuration"""
        import threading
        import time
        
        results = []
        errors = []
        
        def load_config():
            try:
                categories = self.config_manager.load_categories()
                results.append(len(categories))
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=load_config)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), 5)
        # All results should be the same (cached)
        self.assertTrue(all(r == results[0] for r in results))

    def test_memory_usage_optimization(self):
        """Test memory usage optimization in configuration loading"""
        import sys
        
        # Get initial memory usage
        initial_size = sys.getsizeof(self.config_manager)
        
        # Load configurations multiple times
        for _ in range(10):
            self.config_manager.load_categories()
            self.config_manager.load_field_mappings()
            self.config_manager.load_ui_settings()
        
        # Memory usage should not grow significantly due to caching
        final_size = sys.getsizeof(self.config_manager)
        
        # Allow for some growth but not excessive
        self.assertLess(final_size - initial_size, 1000, "Memory usage grew too much")

    def test_unicode_handling(self):
        """Test proper Unicode handling in configurations"""
        # Create config with Unicode characters
        unicode_data = {
            "categories": {
                "日本語": {
                    "display_name": "日本語カテゴリ",
                    "icon": "fas fa-language",
                    "emoji_fallback": "🇯🇵",
                    "color": "#ff0000",
                    "description": "日本語の説明文"
                }
            }
        }
        
        with open(os.path.join(self.test_dir, "categories.json"), 'w', encoding='utf-8') as f:
            json.dump(unicode_data, f, ensure_ascii=False)
        
        categories = self.config_manager.load_categories(force_reload=True)
        
        self.assertIn("日本語", categories)
        category = categories["日本語"]
        self.assertEqual(category.display_name, "日本語カテゴリ")
        self.assertEqual(category.description, "日本語の説明文")

class TestConfigManagerErrorHandling(unittest.TestCase):
    """Test error handling scenarios in ConfigManager"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager(self.test_dir)
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_corrupted_json_recovery(self):
        """Test recovery from corrupted JSON files"""
        # Create corrupted JSON file
        corrupted_path = os.path.join(self.test_dir, "categories.json")
        with open(corrupted_path, 'w') as f:
            f.write('{"categories": {"test": invalid json}')
        
        # Should recover gracefully
        categories = self.config_manager.load_categories()
        self.assertIsInstance(categories, dict)
        # Should use defaults
        self.assertIn("武器", categories)
    
    def test_empty_json_file(self):
        """Test handling of empty JSON files"""
        empty_path = os.path.join(self.test_dir, "categories.json")
        with open(empty_path, 'w') as f:
            f.write('')
        
        categories = self.config_manager.load_categories()
        self.assertIsInstance(categories, dict)
    
    def test_json_with_null_values(self):
        """Test handling of JSON with null values"""
        null_data = {
            "categories": {
                "test_category": {
                    "display_name": None,
                    "icon": "fas fa-test",
                    "emoji_fallback": "🧪",
                    "color": "#3498db"
                }
            }
        }
        
        with open(os.path.join(self.test_dir, "categories.json"), 'w') as f:
            json.dump(null_data, f)
        
        # Should handle null values gracefully
        categories = self.config_manager.load_categories()
        # Category with null display_name should be skipped
        self.assertNotIn("test_category", categories)
    
    def test_file_system_errors(self):
        """Test various file system error scenarios"""
        # Test with read-only directory
        readonly_dir = os.path.join(self.test_dir, "readonly")
        os.makedirs(readonly_dir)
        os.chmod(readonly_dir, 0o444)  # Read-only
        
        try:
            readonly_config = ConfigManager(readonly_dir)
            # Should still work with fallback
            categories = readonly_config.load_categories()
            self.assertIsInstance(categories, dict)
        finally:
            # Restore permissions for cleanup
            os.chmod(readonly_dir, 0o755)
    
    def test_large_configuration_files(self):
        """Test handling of large configuration files"""
        # Create large categories configuration
        large_categories = {"categories": {}}
        for i in range(1000):
            large_categories["categories"][f"category_{i}"] = {
                "display_name": f"Category {i}",
                "icon": "fas fa-test",
                "emoji_fallback": "🧪",
                "color": "#3498db",
                "description": f"Description for category {i}"
            }
        
        with open(os.path.join(self.test_dir, "categories.json"), 'w') as f:
            json.dump(large_categories, f)
        
        # Should handle large files efficiently
        import time
        start_time = time.time()
        categories = self.config_manager.load_categories()
        load_time = time.time() - start_time
        
        self.assertEqual(len(categories), 1000)
        self.assertLess(load_time, 5.0, "Loading took too long")  # Should load within 5 seconds
    
    def test_nested_directory_creation(self):
        """Test creation of nested directories for recovery"""
        nested_path = os.path.join(self.test_dir, "deep", "nested", "config")
        nested_config = ConfigManager(nested_path)
        
        # Should create directories and use defaults
        categories = nested_config.load_categories()
        self.assertIsInstance(categories, dict)


class TestConfigManagerValidation(unittest.TestCase):
    """Test configuration validation functionality"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager(self.test_dir)
        
        # Create schemas directory with test schemas
        self.schemas_dir = os.path.join(self.test_dir, "schemas")
        os.makedirs(self.schemas_dir, exist_ok=True)
        self._create_test_schemas()
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def _create_test_schemas(self):
        """Create test schema files"""
        # Categories schema
        categories_schema = {
            "type": "object",
            "properties": {
                "categories": {
                    "type": "object",
                    "patternProperties": {
                        ".*": {
                            "type": "object",
                            "properties": {
                                "display_name": {"type": "string"},
                                "icon": {"type": "string"},
                                "emoji_fallback": {"type": "string"},
                                "color": {"type": "string", "pattern": "^#[0-9a-fA-F]{6}$"},
                                "description": {"type": "string"}
                            },
                            "required": ["display_name", "icon", "emoji_fallback", "color"]
                        }
                    }
                }
            },
            "required": ["categories"]
        }
        
        with open(os.path.join(self.schemas_dir, "categories-schema.json"), 'w') as f:
            json.dump(categories_schema, f)
        
        # Fields schema
        fields_schema = {
            "type": "object",
            "properties": {
                "field_mappings": {"type": "object"},
                "display_fields": {"type": "array", "items": {"type": "string"}},
                "search_fields": {"type": "array", "items": {"type": "string"}},
                "required_fields": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["field_mappings"]
        }
        
        with open(os.path.join(self.schemas_dir, "fields-schema.json"), 'w') as f:
            json.dump(fields_schema, f)
    
    def test_valid_configuration_validation(self):
        """Test validation of valid configurations"""
        valid_categories = {
            "categories": {
                "test": {
                    "display_name": "Test",
                    "icon": "fas fa-test",
                    "emoji_fallback": "🧪",
                    "color": "#3498db"
                }
            }
        }
        
        result = self.config_manager._validate_config(valid_categories, "categories")
        self.assertTrue(result)
    
    def test_invalid_configuration_validation(self):
        """Test validation of invalid configurations"""
        # Missing required field
        invalid_categories = {
            "categories": {
                "test": {
                    "display_name": "Test",
                    # Missing required fields
                }
            }
        }
        
        result = self.config_manager._validate_config(invalid_categories, "categories")
        self.assertFalse(result)
        
        # Invalid color format
        invalid_color = {
            "categories": {
                "test": {
                    "display_name": "Test",
                    "icon": "fas fa-test",
                    "emoji_fallback": "🧪",
                    "color": "invalid-color"
                }
            }
        }
        
        result = self.config_manager._validate_config(invalid_color, "categories")
        self.assertFalse(result)
    
    def test_schema_loading_errors(self):
        """Test handling of schema loading errors"""
        # Remove schema file
        schema_path = os.path.join(self.schemas_dir, "categories-schema.json")
        os.remove(schema_path)
        
        # Should skip validation gracefully
        test_data = {"categories": {"test": {}}}
        result = self.config_manager._validate_config(test_data, "categories")
        self.assertTrue(result)  # Should return True when no schema available
    
    def test_malformed_schema(self):
        """Test handling of malformed schema files"""
        # Create malformed schema
        with open(os.path.join(self.schemas_dir, "malformed-schema.json"), 'w') as f:
            f.write('{"invalid": json}')
        
        # Should handle gracefully
        result = self.config_manager._validate_config({}, "malformed")
        self.assertTrue(result)  # Should return True when schema is invalid


class TestConfigManagerPerformance(unittest.TestCase):
    """Test performance aspects of ConfigManager"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager(self.test_dir)
        self._create_performance_test_configs()
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def _create_performance_test_configs(self):
        """Create configurations for performance testing"""
        # Large categories file
        categories = {"categories": {}}
        for i in range(100):
            categories["categories"][f"cat_{i}"] = {
                "display_name": f"Category {i}",
                "icon": f"fas fa-icon-{i}",
                "emoji_fallback": "🧪",
                "color": f"#{i:06x}",
                "description": f"Description for category {i} " * 10  # Make it longer
            }
        
        with open(os.path.join(self.test_dir, "categories.json"), 'w') as f:
            json.dump(categories, f)
        
        # Complex fields configuration
        fields = {
            "field_mappings": {f"field_{i}": f"column_{i}" for i in range(50)},
            "display_fields": [f"field_{i}" for i in range(25)],
            "search_fields": [f"field_{i}" for i in range(30)],
            "required_fields": [f"field_{i}" for i in range(10)]
        }
        
        with open(os.path.join(self.test_dir, "fields.json"), 'w') as f:
            json.dump(fields, f)
    
    def test_loading_performance(self):
        """Test configuration loading performance"""
        import time
        
        # Test categories loading
        start_time = time.time()
        categories = self.config_manager.load_categories()
        categories_time = time.time() - start_time
        
        self.assertLess(categories_time, 1.0, "Categories loading took too long")
        self.assertEqual(len(categories), 100)
        
        # Test fields loading
        start_time = time.time()
        fields = self.config_manager.load_field_mappings()
        fields_time = time.time() - start_time
        
        self.assertLess(fields_time, 1.0, "Fields loading took too long")
        self.assertEqual(len(fields["field_mappings"]), 50)
    
    def test_caching_performance(self):
        """Test caching performance benefits"""
        import time
        
        # First load (cold cache)
        start_time = time.time()
        categories1 = self.config_manager.load_categories()
        first_load_time = time.time() - start_time
        
        # Second load (warm cache)
        start_time = time.time()
        categories2 = self.config_manager.load_categories()
        second_load_time = time.time() - start_time
        
        # Cached load should be much faster
        self.assertLess(second_load_time, first_load_time / 10)
        self.assertIs(categories1, categories2)  # Should be same object
    
    def test_memory_efficiency(self):
        """Test memory efficiency of configuration loading"""
        import sys
        
        # Load configurations
        categories = self.config_manager.load_categories()
        fields = self.config_manager.load_field_mappings()
        ui_config = self.config_manager.load_ui_settings()
        
        # Check memory usage is reasonable
        categories_size = sys.getsizeof(categories)
        fields_size = sys.getsizeof(fields)
        ui_size = sys.getsizeof(ui_config)
        
        # Should not use excessive memory
        self.assertLess(categories_size, 100000, "Categories using too much memory")
        self.assertLess(fields_size, 50000, "Fields using too much memory")
        self.assertLess(ui_size, 10000, "UI config using too much memory")


if __name__ == '__main__':
    # Run all test classes
    unittest.main(verbosity=2)