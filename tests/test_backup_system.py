"""
Unit tests for automated backup system.
"""

import unittest
import tempfile
import os
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta

from instant_search_db.data_manager import DataManager
from instant_search_db.config_manager import ConfigManager


class TestBackupSystem(unittest.TestCase):
    """Test cases for automated backup functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, "config")
        self.data_dir = os.path.join(self.temp_dir, "data")
        self.backup_dir = os.path.join(self.temp_dir, "backups")
        
        # Create directories
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create minimal test configuration
        self._create_minimal_config()
        
        # Initialize managers
        self.config_manager = ConfigManager(self.config_dir)
        self.data_manager = DataManager(self.config_manager)
        
        # Override backup directory for testing
        self.data_manager.backup_dir = Path(self.backup_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_minimal_config(self):
        """Create minimal configuration files for testing."""
        # Categories config
        categories_config = {
            "categories": {
                "test": {
                    "display_name": "Test",
                    "icon": "fas fa-test",
                    "emoji_fallback": "🧪",
                    "color": "#3498db",
                    "description": "Test category"
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
                "description": "description"
            },
            "display_fields": ["name", "description"],
            "search_fields": ["name", "description"],
            "required_fields": ["category", "name"],
            "field_definitions": {
                "category": {
                    "display_name": "Category",
                    "type": "string",
                    "required": True
                },
                "name": {
                    "display_name": "Name",
                    "type": "string",
                    "required": True
                },
                "description": {
                    "display_name": "Description",
                    "type": "text",
                    "required": False
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
    
    def _create_test_file(self, filename: str, content: str = "test content") -> str:
        """Create a test file and return its path."""
        file_path = os.path.join(self.data_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    
    def _create_test_directory(self, dirname: str) -> str:
        """Create a test directory with some files and return its path."""
        dir_path = os.path.join(self.data_dir, dirname)
        os.makedirs(dir_path, exist_ok=True)
        
        # Add some test files
        with open(os.path.join(dir_path, "file1.txt"), 'w') as f:
            f.write("test file 1")
        with open(os.path.join(dir_path, "file2.txt"), 'w') as f:
            f.write("test file 2")
        
        return dir_path
    
    def test_setup_backup_directory_structure(self):
        """Test backup directory structure setup."""
        self.data_manager.setup_backup_directory_structure()
        
        # Check main backup directory exists
        self.assertTrue(os.path.exists(self.backup_dir))
        
        # Check subdirectories exist
        expected_subdirs = ['data', 'config', 'database', 'full_system']
        for subdir in expected_subdirs:
            subdir_path = os.path.join(self.backup_dir, subdir)
            self.assertTrue(os.path.exists(subdir_path), f"Subdirectory {subdir} not found")
        
        # Check retention policy file exists
        retention_policy_path = os.path.join(self.backup_dir, "retention_policy.json")
        self.assertTrue(os.path.exists(retention_policy_path))
        
        # Verify retention policy content
        with open(retention_policy_path, 'r') as f:
            policy = json.load(f)
        
        self.assertIn("retention_rules", policy)
        self.assertIn("daily_backups", policy["retention_rules"])
        self.assertIn("weekly_backups", policy["retention_rules"])
        self.assertIn("monthly_backups", policy["retention_rules"])
    
    def test_create_automatic_backup_file(self):
        """Test creating automatic backup of a file."""
        # Create test file
        test_file = self._create_test_file("test.csv", "category,name,description\ntest,Test Item,Test description")
        
        # Create backup
        backup_path = self.data_manager.create_automatic_backup(test_file, "data", "Test backup")
        
        # Verify backup was created
        self.assertTrue(os.path.exists(backup_path))
        
        # Verify backup content matches original
        with open(backup_path, 'r') as f:
            backup_content = f.read()
        with open(test_file, 'r') as f:
            original_content = f.read()
        
        self.assertEqual(backup_content, original_content)
        
        # Verify metadata file exists
        backup_name = os.path.basename(backup_path)
        metadata_path = os.path.join(os.path.dirname(backup_path), f"{backup_name}_metadata.json")
        self.assertTrue(os.path.exists(metadata_path))
        
        # Verify metadata content
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        self.assertEqual(metadata["backup_type"], "data")
        self.assertEqual(metadata["file_type"], "file")
        self.assertEqual(metadata["description"], "Test backup")
        self.assertIn("backup_id", metadata)
        self.assertIn("created_at", metadata)
        self.assertIn("size_bytes", metadata)
        self.assertIn("checksum", metadata)
    
    def test_create_automatic_backup_directory(self):
        """Test creating automatic backup of a directory."""
        # Create test directory
        test_dir = self._create_test_directory("test_dir")
        
        # Create backup
        backup_path = self.data_manager.create_automatic_backup(test_dir, "config", "Directory backup")
        
        # Verify backup was created
        self.assertTrue(os.path.exists(backup_path))
        self.assertTrue(os.path.isdir(backup_path))
        
        # Verify backup contains original files
        original_files = set(os.listdir(test_dir))
        backup_files = set(os.listdir(backup_path))
        self.assertEqual(original_files, backup_files)
        
        # Verify metadata
        backup_name = os.path.basename(backup_path)
        metadata_path = os.path.join(os.path.dirname(backup_path), f"{backup_name}_metadata.json")
        self.assertTrue(os.path.exists(metadata_path))
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        self.assertEqual(metadata["backup_type"], "config")
        self.assertEqual(metadata["file_type"], "directory")
        self.assertGreater(metadata["size_bytes"], 0)
    
    def test_backup_index_update(self):
        """Test backup index is properly updated."""
        # Create test file and backup
        test_file = self._create_test_file("test.txt", "test content")
        backup_path = self.data_manager.create_automatic_backup(test_file, "data")
        
        # Check backup index exists
        index_path = os.path.join(self.backup_dir, "backup_index.json")
        self.assertTrue(os.path.exists(index_path))
        
        # Verify index content
        with open(index_path, 'r') as f:
            index = json.load(f)
        
        self.assertIn("backups", index)
        self.assertIn("last_updated", index)
        self.assertEqual(len(index["backups"]), 1)
        
        backup_entry = index["backups"][0]
        self.assertEqual(backup_entry["backup_type"], "data")
        self.assertIn("backup_id", backup_entry)
        self.assertIn("created_at", backup_entry)
    
    def test_pre_update_backup(self):
        """Test pre-update backup creation."""
        # Create test data file
        test_file = self._create_test_file("data.csv", "category,name\ntest,Test Item")
        
        # Create pre-update backup
        backup_path = self.data_manager.create_pre_update_backup(test_file, "Before data update")
        
        # Verify backup was created
        self.assertTrue(os.path.exists(backup_path))
        
        # Verify it's in the data subdirectory
        self.assertIn("data", backup_path)
        
        # Verify metadata contains correct description
        backup_name = os.path.basename(backup_path)
        metadata_path = os.path.join(os.path.dirname(backup_path), f"{backup_name}_metadata.json")
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        self.assertEqual(metadata["description"], "Before data update")
    
    def test_backup_statistics(self):
        """Test backup statistics generation."""
        # Create multiple backups
        test_file1 = self._create_test_file("test1.txt", "content 1")
        test_file2 = self._create_test_file("test2.txt", "content 2")
        test_dir = self._create_test_directory("test_dir")
        
        self.data_manager.create_automatic_backup(test_file1, "data")
        self.data_manager.create_automatic_backup(test_file2, "config")
        self.data_manager.create_automatic_backup(test_dir, "database")
        
        # Get statistics
        stats = self.data_manager.get_backup_statistics()
        
        # Verify statistics
        self.assertEqual(stats["total_backups"], 3)
        self.assertGreater(stats["total_size_mb"], 0)
        
        # Check backup type distribution
        self.assertEqual(stats["backup_types"]["data"], 1)
        self.assertEqual(stats["backup_types"]["config"], 1)
        self.assertEqual(stats["backup_types"]["database"], 1)
        
        # Check date fields exist
        self.assertIsNotNone(stats["oldest_backup"])
        self.assertIsNotNone(stats["newest_backup"])
    
    def test_cleanup_old_backups(self):
        """Test cleanup of old backups based on retention policy."""
        # Create backup directory structure
        self.data_manager.setup_backup_directory_structure()
        
        # Create test file
        test_file = self._create_test_file("test.txt", "test content")
        
        # Create backup
        backup_path = self.data_manager.create_automatic_backup(test_file, "data")
        
        # Manually modify backup metadata to make it appear old
        backup_name = os.path.basename(backup_path)
        metadata_path = os.path.join(os.path.dirname(backup_path), f"{backup_name}_metadata.json")
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Make backup appear 10 days old (should be cleaned up with default 7-day retention)
        old_date = (datetime.now() - timedelta(days=10)).isoformat()
        metadata["created_at"] = old_date
        metadata["retention_category"] = "daily"
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Update backup index with old date
        index_path = os.path.join(self.backup_dir, "backup_index.json")
        with open(index_path, 'r') as f:
            index = json.load(f)
        
        index["backups"][0]["created_at"] = old_date
        index["backups"][0]["retention_category"] = "daily"
        
        with open(index_path, 'w') as f:
            json.dump(index, f, indent=2)
        
        # Perform cleanup
        cleanup_stats = self.data_manager.cleanup_old_backups()
        
        # Verify cleanup occurred
        self.assertEqual(cleanup_stats["files_removed"], 1)
        self.assertGreater(cleanup_stats["space_freed_mb"], 0)
        
        # Verify backup file was removed
        self.assertFalse(os.path.exists(backup_path))
        self.assertFalse(os.path.exists(metadata_path))
    
    def test_backup_nonexistent_file(self):
        """Test backup creation fails gracefully for nonexistent files."""
        with self.assertRaises(FileNotFoundError):
            self.data_manager.create_automatic_backup("/nonexistent/file.txt", "data")
    
    def test_retention_category_determination(self):
        """Test retention category determination logic."""
        # This is a private method, but we can test it indirectly
        test_file = self._create_test_file("test.txt", "test content")
        backup_path = self.data_manager.create_automatic_backup(test_file, "data")
        
        # Check metadata for retention category
        backup_name = os.path.basename(backup_path)
        metadata_path = os.path.join(os.path.dirname(backup_path), f"{backup_name}_metadata.json")
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Should be one of the valid retention categories
        self.assertIn(metadata["retention_category"], ["daily", "weekly", "monthly"])


if __name__ == '__main__':
    unittest.main()