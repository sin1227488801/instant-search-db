"""
Unit tests for DataManager class.
"""

import unittest
import tempfile
import os
import json
import csv
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from instant_search_db.data_manager import DataManager
from instant_search_db.data_models import Item, ValidationResult, DataStats
from instant_search_db.config_manager import ConfigManager


class TestDataManager(unittest.TestCase):
    """Test cases for DataManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock config manager
        self.mock_config_manager = Mock(spec=ConfigManager)
        self.mock_config_manager.load_field_mappings.return_value = {
            'field_mappings': {
                'category': 'category',
                'name': 'name',
                'description': 'description',
                'attack': 'attack',
                'price': 'price'
            },
            'required_fields': ['category', 'name'],
            'field_definitions': {
                'category': {'type': 'string', 'required': True},
                'name': {'type': 'string', 'required': True},
                'description': {'type': 'text', 'required': False},
                'attack': {'type': 'integer', 'min_value': 0},
                'price': {'type': 'integer', 'min_value': 0}
            }
        }
        
        self.data_manager = DataManager(self.mock_config_manager)
        
        # Create temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()
        self.data_manager.backup_dir = Path(self.temp_dir) / "backups"
        self.data_manager.backup_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_init(self):
        """Test DataManager initialization."""
        self.assertEqual(self.data_manager.config_manager, self.mock_config_manager)
        self.assertTrue(self.data_manager.backup_dir.exists())
    
    def test_load_data_with_mapping_file_not_found(self):
        """Test loading data when CSV file doesn't exist."""
        items, validation_result = self.data_manager.load_data_with_mapping("nonexistent.csv")
        
        self.assertEqual(len(items), 0)
        self.assertFalse(validation_result.is_valid)
        self.assertIn("CSV file not found", validation_result.errors[0])
    
    def test_load_data_with_mapping_success(self):
        """Test successful data loading with field mapping."""
        # Create temporary CSV file
        csv_content = """category,name,description,attack,price
武器,つるはし,壁を掘れる,1,240
盾,皮甲の盾,錆びない,0,1000
"""
        csv_path = os.path.join(self.temp_dir, "test.csv")
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        items, validation_result = self.data_manager.load_data_with_mapping(csv_path)
        
        self.assertEqual(len(items), 2)
        self.assertTrue(validation_result.is_valid)
        
        # Check first item
        item1 = items[0]
        self.assertEqual(item1.category, "武器")
        self.assertEqual(item1.name, "つるはし")
        self.assertEqual(item1.description, "壁を掘れる")
        self.assertEqual(item1.custom_fields['attack'], 1)
        self.assertEqual(item1.custom_fields['price'], 240)
        
        # Check second item
        item2 = items[1]
        self.assertEqual(item2.category, "盾")
        self.assertEqual(item2.name, "皮甲の盾")
        self.assertEqual(item2.description, "錆びない")
        self.assertEqual(item2.custom_fields['attack'], 0)
        self.assertEqual(item2.custom_fields['price'], 1000)
    
    def test_load_data_with_mapping_missing_columns(self):
        """Test loading data with missing CSV columns."""
        # Create CSV with missing columns
        csv_content = """category,name
武器,つるはし
"""
        csv_path = os.path.join(self.temp_dir, "test.csv")
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        items, validation_result = self.data_manager.load_data_with_mapping(csv_path)
        
        self.assertEqual(len(items), 1)
        self.assertTrue(validation_result.is_valid)  # Should still be valid with warnings
        self.assertTrue(len(validation_result.warnings) > 0)
        
        # Check that warnings mention missing columns
        warning_text = ' '.join(validation_result.warnings)
        self.assertIn("missing CSV column", warning_text)
    
    def test_convert_field_value_types(self):
        """Test field value type conversion."""
        # Test integer conversion
        self.assertEqual(self.data_manager._convert_field_value("123", "attack"), 123)
        
        # Test boolean conversion
        self.assertTrue(self.data_manager._convert_field_value("true", "sellable"))
        self.assertTrue(self.data_manager._convert_field_value("○", "sellable"))
        self.assertFalse(self.data_manager._convert_field_value("false", "sellable"))
        
        # Test string fallback for invalid conversion
        self.assertEqual(self.data_manager._convert_field_value("invalid_number", "attack"), "invalid_number")
        
        # Test empty value
        self.assertIsNone(self.data_manager._convert_field_value("", "attack"))
    
    def test_validate_data_success(self):
        """Test successful data validation."""
        items = [
            Item(category="武器", name="つるはし", description="壁を掘れる", 
                 custom_fields={"attack": 1, "price": 240}),
            Item(category="盾", name="皮甲の盾", description="錆びない", 
                 custom_fields={"attack": 0, "price": 1000})
        ]
        
        validation_result = self.data_manager.validate_data(items)
        
        self.assertTrue(validation_result.is_valid)
        self.assertEqual(len(validation_result.errors), 0)
    
    def test_validate_data_missing_required_fields(self):
        """Test validation with missing required fields."""
        items = [
            Item(category="", name="つるはし"),  # Missing category
            Item(category="武器", name="")       # Missing name
        ]
        
        validation_result = self.data_manager.validate_data(items)
        
        self.assertFalse(validation_result.is_valid)
        self.assertTrue(len(validation_result.errors) >= 2)
        
        error_text = ' '.join(validation_result.errors)
        self.assertIn("Missing required field 'category'", error_text)
        self.assertIn("Missing required field 'name'", error_text)
    
    def test_validate_data_type_errors(self):
        """Test validation with type errors."""
        items = [
            Item(category="武器", name="つるはし", 
                 custom_fields={"attack": "not_a_number"})  # Invalid integer
        ]
        
        validation_result = self.data_manager.validate_data(items)
        
        self.assertFalse(validation_result.is_valid)
        error_text = ' '.join(validation_result.errors)
        self.assertIn("invalid type", error_text)
    
    def test_validate_field_type(self):
        """Test field type validation."""
        # Test string validation
        self.assertTrue(self.data_manager._validate_field_type("test", "string"))
        self.assertFalse(self.data_manager._validate_field_type(123, "string"))
        
        # Test integer validation
        self.assertTrue(self.data_manager._validate_field_type(123, "integer"))
        self.assertFalse(self.data_manager._validate_field_type("123", "integer"))
        
        # Test float validation
        self.assertTrue(self.data_manager._validate_field_type(123.45, "float"))
        self.assertTrue(self.data_manager._validate_field_type(123, "float"))  # int is valid for float
        self.assertFalse(self.data_manager._validate_field_type("123.45", "float"))
        
        # Test boolean validation
        self.assertTrue(self.data_manager._validate_field_type(True, "boolean"))
        self.assertFalse(self.data_manager._validate_field_type("true", "boolean"))
        
        # Test unknown type (should return True)
        self.assertTrue(self.data_manager._validate_field_type("anything", "unknown_type"))
    
    def test_create_backup_file(self):
        """Test creating backup of a file."""
        # Create test file
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        backup_path = self.data_manager.create_backup(test_file)
        
        self.assertTrue(os.path.exists(backup_path))
        
        # Check backup content
        with open(backup_path, 'r') as f:
            content = f.read()
        self.assertEqual(content, "test content")
        
        # Check metadata file exists
        metadata_path = Path(backup_path).parent / f"{Path(backup_path).name}_metadata.json"
        self.assertTrue(metadata_path.exists())
        
        # Check metadata content
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        self.assertEqual(metadata['source_path'], test_file)
        self.assertEqual(metadata['backup_type'], 'file')
    
    def test_create_backup_directory(self):
        """Test creating backup of a directory."""
        # Create test directory with files
        test_dir = os.path.join(self.temp_dir, "test_dir")
        os.makedirs(test_dir)
        
        test_file = os.path.join(test_dir, "file.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        backup_path = self.data_manager.create_backup(test_dir)
        
        self.assertTrue(os.path.exists(backup_path))
        self.assertTrue(os.path.isdir(backup_path))
        
        # Check backup content
        backup_file = os.path.join(backup_path, "file.txt")
        self.assertTrue(os.path.exists(backup_file))
        
        with open(backup_file, 'r') as f:
            content = f.read()
        self.assertEqual(content, "test content")
    
    def test_create_backup_nonexistent_source(self):
        """Test creating backup of nonexistent source."""
        with self.assertRaises(FileNotFoundError):
            self.data_manager.create_backup("nonexistent_file.txt")
    
    def test_get_data_statistics(self):
        """Test generating data statistics."""
        items = [
            Item(category="武器", name="つるはし", custom_fields={"attack": 1}),
            Item(category="武器", name="剣", custom_fields={"attack": 2}),
            Item(category="盾", name="皮甲の盾", custom_fields={"defense": 1}),
        ]
        
        stats = self.data_manager.get_data_statistics(items)
        
        self.assertEqual(stats.total_items, 3)
        self.assertEqual(stats.categories["武器"], 2)
        self.assertEqual(stats.categories["盾"], 1)
        self.assertIn("attack", stats.custom_fields)
        self.assertIn("defense", stats.custom_fields)
        self.assertIn("id", stats.fields)
        self.assertIn("category", stats.fields)
        self.assertIn("name", stats.fields)
    
    def test_list_backups(self):
        """Test listing available backups."""
        # Create test backup metadata
        metadata1 = {
            "source_path": "test1.txt",
            "backup_path": "backup1",
            "created_at": "2024-01-01T10:00:00",
            "backup_type": "file"
        }
        
        metadata2 = {
            "source_path": "test2.txt", 
            "backup_path": "backup2",
            "created_at": "2024-01-02T10:00:00",
            "backup_type": "file"
        }
        
        # Write metadata files
        with open(self.data_manager.backup_dir / "backup1_metadata.json", 'w') as f:
            json.dump(metadata1, f)
        
        with open(self.data_manager.backup_dir / "backup2_metadata.json", 'w') as f:
            json.dump(metadata2, f)
        
        backups = self.data_manager.list_backups()
        
        self.assertEqual(len(backups), 2)
        # Should be sorted by date (newest first)
        self.assertEqual(backups[0]['created_at'], "2024-01-02T10:00:00")
        self.assertEqual(backups[1]['created_at'], "2024-01-01T10:00:00")
    
    def test_restore_backup_file(self):
        """Test restoring a file backup."""
        # Create backup file
        backup_content = "backup content"
        backup_file = os.path.join(self.temp_dir, "backup.txt")
        with open(backup_file, 'w') as f:
            f.write(backup_content)
        
        # Restore to new location
        target_file = os.path.join(self.temp_dir, "restored.txt")
        result = self.data_manager.restore_backup(backup_file, target_file)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(target_file))
        
        with open(target_file, 'r') as f:
            content = f.read()
        self.assertEqual(content, backup_content)
    
    def test_restore_backup_nonexistent(self):
        """Test restoring nonexistent backup."""
        result = self.data_manager.restore_backup("nonexistent_backup", "target")
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()