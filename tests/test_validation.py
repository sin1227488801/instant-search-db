"""
Unit tests for data validation system.
"""

import unittest
import tempfile
import os
import json
from pathlib import Path

from instant_search_db.data_manager import DataManager
from instant_search_db.config_manager import ConfigManager
from instant_search_db.data_models import Item, ValidationResult


class TestDataValidation(unittest.TestCase):
    """Test cases for data validation functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, "config")
        self.data_dir = os.path.join(self.temp_dir, "data")
        
        # Create directories
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create test configuration files
        self._create_test_configs()
        
        # Initialize managers
        self.config_manager = ConfigManager(self.config_dir)
        self.data_manager = DataManager(self.config_manager)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_test_configs(self):
        """Create test configuration files."""
        # Categories config
        categories_config = {
            "categories": {
                "weapon": {
                    "display_name": "Weapon",
                    "icon": "fas fa-sword",
                    "emoji_fallback": "⚔️",
                    "color": "#e74c3c",
                    "description": "Weapons"
                },
                "shield": {
                    "display_name": "Shield",
                    "icon": "fas fa-shield",
                    "emoji_fallback": "🛡️",
                    "color": "#3498db",
                    "description": "Shields"
                }
            }
        }
        
        with open(os.path.join(self.config_dir, "categories.json"), 'w') as f:
            json.dump(categories_config, f)
        
        # Fields config
        fields_config = {
            "field_mappings": {
                "category": "category",
                "name": "name",
                "description": "description",
                "price": "price"
            },
            "display_fields": ["name", "description", "price"],
            "search_fields": ["name", "description"],
            "required_fields": ["category", "name"],
            "field_definitions": {
                "category": {
                    "display_name": "Category",
                    "type": "string",
                    "required": True,
                    "max_length": 50
                },
                "name": {
                    "display_name": "Name",
                    "type": "string",
                    "required": True,
                    "min_length": 1,
                    "max_length": 100
                },
                "description": {
                    "display_name": "Description",
                    "type": "text",
                    "required": False,
                    "max_length": 500
                },
                "price": {
                    "display_name": "Price",
                    "type": "integer",
                    "required": False,
                    "min_value": 0,
                    "max_value": 999999
                }
            }
        }
        
        with open(os.path.join(self.config_dir, "fields.json"), 'w') as f:
            json.dump(fields_config, f)
        
        # UI config
        ui_config = {
            "ui": {
                "title": "Test System",
                "subtitle": "Test subtitle"
            }
        }
        
        with open(os.path.join(self.config_dir, "ui.json"), 'w') as f:
            json.dump(ui_config, f)
        
        # Validation config
        validation_config = {
            "validation_rules": {
                "required_columns": ["category", "name"],
                "field_types": {
                    "category": {
                        "type": "string",
                        "required": True,
                        "allowed_values": ["weapon", "shield"]
                    },
                    "name": {
                        "type": "string",
                        "required": True,
                        "min_length": 1,
                        "max_length": 100
                    },
                    "description": {
                        "type": "text",
                        "required": False,
                        "max_length": 500
                    },
                    "price": {
                        "type": "integer",
                        "required": False,
                        "min_value": 0
                    }
                },
                "data_quality": {
                    "allow_empty_values": False,
                    "trim_whitespace": True,
                    "normalize_case": "none",
                    "duplicate_handling": "warn"
                },
                "custom_validators": [
                    {
                        "name": "category_check",
                        "field": "category",
                        "rule": "must_exist_in_categories_config",
                        "message": "Category must be valid"
                    }
                ]
            }
        }
        
        with open(os.path.join(self.data_dir, "validation.json"), 'w') as f:
            json.dump(validation_config, f)
    
    def _create_test_csv(self, filename: str, content: str):
        """Create a test CSV file."""
        csv_path = os.path.join(self.data_dir, filename)
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return csv_path
    
    def test_csv_structure_validation_valid(self):
        """Test CSV structure validation with valid file."""
        csv_content = "category,name,description,price\nweapon,Sword,A sharp blade,100\nshield,Shield,Protective gear,50"
        csv_path = self._create_test_csv("valid.csv", csv_content)
        
        result = self.data_manager.validate_csv_structure(csv_path)
        
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
    
    def test_csv_structure_validation_missing_required(self):
        """Test CSV structure validation with missing required columns."""
        csv_content = "name,description,price\nSword,A sharp blade,100"
        csv_path = self._create_test_csv("missing_required.csv", csv_content)
        
        result = self.data_manager.validate_csv_structure(csv_path)
        
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Required column 'category' not found" in error for error in result.errors))
    
    def test_csv_structure_validation_empty_file(self):
        """Test CSV structure validation with empty file."""
        csv_path = self._create_test_csv("empty.csv", "")
        
        result = self.data_manager.validate_csv_structure(csv_path)
        
        self.assertFalse(result.is_valid)
        self.assertTrue(any("empty" in error.lower() for error in result.errors))
    
    def test_field_value_validation_string(self):
        """Test field value validation for string fields."""
        field_rules = {
            "type": "string",
            "required": True,
            "min_length": 2,
            "max_length": 10,
            "pattern": r"^[A-Za-z]+$"
        }
        
        # Valid value
        errors = self.data_manager.validate_field_value("test_field", "Valid", field_rules, 1)
        self.assertEqual(len(errors), 0)
        
        # Too short
        errors = self.data_manager.validate_field_value("test_field", "A", field_rules, 1)
        self.assertTrue(any("too short" in error for error in errors))
        
        # Too long
        errors = self.data_manager.validate_field_value("test_field", "TooLongValue", field_rules, 1)
        self.assertTrue(any("too long" in error for error in errors))
        
        # Invalid pattern
        errors = self.data_manager.validate_field_value("test_field", "Invalid123", field_rules, 1)
        self.assertTrue(any("pattern" in error for error in errors))
        
        # Empty required field
        errors = self.data_manager.validate_field_value("test_field", "", field_rules, 1)
        self.assertTrue(any("empty" in error for error in errors))
    
    def test_field_value_validation_integer(self):
        """Test field value validation for integer fields."""
        field_rules = {
            "type": "integer",
            "required": False,
            "min_value": 0,
            "max_value": 1000
        }
        
        # Valid value
        errors = self.data_manager.validate_field_value("price", 100, field_rules, 1)
        self.assertEqual(len(errors), 0)
        
        # Below minimum
        errors = self.data_manager.validate_field_value("price", -10, field_rules, 1)
        self.assertTrue(any("minimum" in error for error in errors))
        
        # Above maximum
        errors = self.data_manager.validate_field_value("price", 2000, field_rules, 1)
        self.assertTrue(any("maximum" in error for error in errors))
        
        # Wrong type
        errors = self.data_manager.validate_field_value("price", "not_a_number", field_rules, 1)
        self.assertTrue(any("invalid type" in error for error in errors))
    
    def test_field_value_validation_allowed_values(self):
        """Test field value validation with allowed values."""
        field_rules = {
            "type": "string",
            "required": True,
            "allowed_values": ["weapon", "shield", "potion"]
        }
        
        # Valid value
        errors = self.data_manager.validate_field_value("category", "weapon", field_rules, 1)
        self.assertEqual(len(errors), 0)
        
        # Invalid value
        errors = self.data_manager.validate_field_value("category", "invalid", field_rules, 1)
        self.assertTrue(any("invalid value" in error for error in errors))
    
    def test_comprehensive_data_validation(self):
        """Test comprehensive data validation."""
        # Create test items
        items = [
            Item(category="weapon", name="Sword", description="A sharp blade", custom_fields={"price": 100}),
            Item(category="shield", name="Shield", description="Protective gear", custom_fields={"price": 50}),
            Item(category="invalid", name="", description="", custom_fields={"price": -10})  # Invalid item
        ]
        
        result = self.data_manager.validate_data_comprehensive(items)
        
        # Should have errors for the invalid item
        self.assertFalse(result.is_valid)
        self.assertTrue(len(result.errors) > 0)
        
        # Check specific error types
        error_text = " ".join(result.errors)
        self.assertIn("invalid value", error_text.lower())  # Invalid category
        self.assertIn("empty", error_text.lower())  # Empty required field
    
    def test_custom_validator_category_consistency(self):
        """Test custom validator for category consistency."""
        item = Item(category="nonexistent", name="Test Item")
        
        validator = {
            "name": "category_check",
            "field": "category",
            "rule": "must_exist_in_categories_config",
            "message": "Category must be valid"
        }
        
        validation_result = ValidationResult(is_valid=True)
        self.data_manager._apply_custom_validator(item, validator, 1, validation_result)
        
        self.assertFalse(validation_result.is_valid)
        self.assertTrue(any("Category must be valid" in error for error in validation_result.errors))
    
    def test_validation_report_generation(self):
        """Test validation report generation."""
        validation_result = ValidationResult(is_valid=False)
        validation_result.add_error("Test error 1")
        validation_result.add_error("Test error 2")
        validation_result.add_warning("Test warning 1")
        
        report = self.data_manager.generate_validation_report(validation_result)
        
        self.assertIn("DATA VALIDATION REPORT", report)
        self.assertIn("FAILED", report)
        self.assertIn("Test error 1", report)
        self.assertIn("Test error 2", report)
        self.assertIn("Test warning 1", report)
        self.assertIn("RECOMMENDATIONS", report)
    
    def test_data_loading_with_validation(self):
        """Test data loading with validation."""
        csv_content = "category,name,description,price\nweapon,Sword,A sharp blade,100\nshield,Shield,Protective gear,50"
        csv_path = self._create_test_csv("test_data.csv", csv_content)
        
        items, validation_result = self.data_manager.load_data_with_mapping(csv_path)
        
        self.assertTrue(validation_result.is_valid)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].category, "weapon")
        self.assertEqual(items[0].name, "Sword")
        self.assertEqual(items[0].custom_fields.get("price"), 100)


if __name__ == '__main__':
    unittest.main()