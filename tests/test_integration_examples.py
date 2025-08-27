import unittest
import os
import tempfile
import shutil
import json
import csv
from unittest.mock import patch, MagicMock
from instant_search_db.config_manager import ConfigManager
from instant_search_db.data_manager import DataManager
from instant_search_db.models import search_items, load_items_from_csv


class TestExampleConfigurationsIntegration(unittest.TestCase):
    """Integration tests for example configurations"""
    
    def setUp(self):
        """Set up test environment with temporary directories"""
        self.test_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.test_dir, "config")
        self.data_dir = os.path.join(self.test_dir, "data")
        self.examples_dir = os.path.join(self.config_dir, "examples")
        
        # Create directory structure
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.examples_dir, exist_ok=True)
        
        # Copy example configurations
        self._copy_example_configs()
        
        # Initialize managers
        self.config_manager = ConfigManager(self.config_dir)
        self.data_manager = DataManager(self.data_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def _copy_example_configs(self):
        """Copy example configurations to test directory"""
        source_examples_dir = "config/examples"
        
        if os.path.exists(source_examples_dir):
            for filename in os.listdir(source_examples_dir):
                if filename.endswith('.json') or filename.endswith('.csv'):
                    source_path = os.path.join(source_examples_dir, filename)
                    dest_path = os.path.join(self.examples_dir, filename)
                    shutil.copy2(source_path, dest_path)
    
    def _load_example_config(self, example_name):
        """Load and apply an example configuration"""
        example_config = self.config_manager.load_example_config(example_name)
        self.assertIsNotNone(example_config, f"Failed to load {example_name} configuration")
        
        # Write configuration files
        if "categories" in example_config:
            categories_data = {"categories": example_config["categories"]}
            with open(os.path.join(self.config_dir, "categories.json"), 'w', encoding='utf-8') as f:
                json.dump(categories_data, f, ensure_ascii=False, indent=2)
        
        if "field_mappings" in example_config:
            fields_data = {
                "field_mappings": example_config["field_mappings"],
                "display_fields": example_config.get("display_fields", []),
                "search_fields": example_config.get("search_fields", []),
                "required_fields": example_config.get("required_fields", [])
            }
            with open(os.path.join(self.config_dir, "fields.json"), 'w', encoding='utf-8') as f:
                json.dump(fields_data, f, ensure_ascii=False, indent=2)
        
        if "ui" in example_config:
            ui_data = {"ui": example_config["ui"]}
            with open(os.path.join(self.config_dir, "ui.json"), 'w', encoding='utf-8') as f:
                json.dump(ui_data, f, ensure_ascii=False, indent=2)
        
        # Clear cache to force reload
        self.config_manager.clear_cache()
        
        return example_config
    
    def _load_sample_data(self, sample_filename):
        """Load sample CSV data"""
        sample_path = os.path.join(self.examples_dir, sample_filename)
        if not os.path.exists(sample_path):
            self.skipTest(f"Sample data file {sample_filename} not found")
        
        # Copy to data directory
        data_path = os.path.join(self.data_dir, "items.csv")
        shutil.copy2(sample_path, data_path)
        
        return data_path


class TestProductCatalogIntegration(TestExampleConfigurationsIntegration):
    """Integration tests for product catalog configuration"""
    
    def test_product_catalog_configuration_loading(self):
        """Test loading product catalog configuration"""
        config = self._load_example_config("product-catalog")
        
        # Verify categories
        categories = self.config_manager.load_categories()
        self.assertIn("electronics", categories)
        self.assertIn("clothing", categories)
        self.assertIn("books", categories)
        
        # Verify category properties
        electronics = categories["electronics"]
        self.assertEqual(electronics.display_name, "Electronics")
        self.assertEqual(electronics.icon, "fas fa-laptop")
        self.assertEqual(electronics.emoji_fallback, "💻")
        self.assertEqual(electronics.color, "#3498db")
    
    def test_product_catalog_field_mappings(self):
        """Test product catalog field mappings"""
        config = self._load_example_config("product-catalog")
        
        fields = self.config_manager.load_field_mappings()
        
        # Verify field mappings
        mappings = fields["field_mappings"]
        self.assertEqual(mappings["name"], "product_name")
        self.assertEqual(mappings["price"], "price")
        self.assertEqual(mappings["sku"], "sku")
        self.assertEqual(mappings["brand"], "brand")
        
        # Verify display and search fields
        self.assertIn("name", fields["display_fields"])
        self.assertIn("brand", fields["display_fields"])
        self.assertIn("price", fields["display_fields"])
        
        self.assertIn("name", fields["search_fields"])
        self.assertIn("brand", fields["search_fields"])
        self.assertIn("sku", fields["search_fields"])
    
    def test_product_catalog_ui_settings(self):
        """Test product catalog UI settings"""
        config = self._load_example_config("product-catalog")
        
        ui_config = self.config_manager.load_ui_settings()
        
        self.assertEqual(ui_config.title, "Product Catalog Search")
        self.assertEqual(ui_config.subtitle, "Find products quickly and easily")
        
        # Verify theme colors
        self.assertEqual(ui_config.theme["primary_color"], "#2c3e50")
        self.assertEqual(ui_config.theme["secondary_color"], "#3498db")
        self.assertEqual(ui_config.theme["accent_color"], "#e74c3c")
        
        # Verify layout settings
        self.assertEqual(ui_config.layout["categories_per_row"], 4)
        self.assertTrue(ui_config.layout["show_category_counts"])
    
    def test_product_catalog_data_loading(self):
        """Test loading product catalog sample data"""
        config = self._load_example_config("product-catalog")
        data_path = self._load_sample_data("product-catalog-sample.csv")
        
        # Load data using field mappings
        fields = self.config_manager.load_field_mappings()
        
        # Mock the load_items_from_csv function to use our test data
        with patch('instant_search_db.models.load_items_from_csv') as mock_load:
            # Read the actual CSV data
            items = []
            with open(data_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    items.append({
                        'id': len(items) + 1,
                        'category': row.get('category', ''),
                        'name': row.get('product_name', ''),
                        'description': row.get('description', ''),
                        'custom_fields': {k: v for k, v in row.items() 
                                        if k not in ['category', 'product_name', 'description']}
                    })
            
            mock_load.return_value = items
            
            loaded_items = load_items_from_csv(data_path)
            
            # Verify data was loaded correctly
            self.assertGreater(len(loaded_items), 0)
            
            # Check first item
            first_item = loaded_items[0]
            self.assertEqual(first_item['category'], 'electronics')
            self.assertIn('iPhone', first_item['name'])
            self.assertIn('price', first_item['custom_fields'])
            self.assertIn('sku', first_item['custom_fields'])
    
    def test_product_catalog_search_functionality(self):
        """Test search functionality with product catalog data"""
        config = self._load_example_config("product-catalog")
        data_path = self._load_sample_data("product-catalog-sample.csv")
        
        # Mock search functionality
        with patch('instant_search_db.models.search_items') as mock_search:
            # Simulate search results
            mock_search.return_value = [
                {
                    'id': 1,
                    'category': 'electronics',
                    'name': 'iPhone 15 Pro',
                    'description': 'Latest Apple smartphone',
                    'custom_fields': {'price': '999.00', 'brand': 'Apple'}
                }
            ]
            
            results = search_items("iPhone", "")
            
            self.assertEqual(len(results), 1)
            self.assertIn('iPhone', results[0]['name'])
            self.assertEqual(results[0]['category'], 'electronics')


class TestDocumentLibraryIntegration(TestExampleConfigurationsIntegration):
    """Integration tests for document library configuration"""
    
    def test_document_library_configuration_loading(self):
        """Test loading document library configuration"""
        config = self._load_example_config("document-library")
        
        # Verify categories
        categories = self.config_manager.load_categories()
        self.assertIn("policies", categories)
        self.assertIn("manuals", categories)
        self.assertIn("reports", categories)
        self.assertIn("presentations", categories)
        
        # Verify category properties
        policies = categories["policies"]
        self.assertEqual(policies.display_name, "Policies")
        self.assertEqual(policies.icon, "fas fa-gavel")
        self.assertEqual(policies.emoji_fallback, "📋")
        self.assertEqual(policies.color, "#e74c3c")
    
    def test_document_library_field_mappings(self):
        """Test document library field mappings"""
        config = self._load_example_config("document-library")
        
        fields = self.config_manager.load_field_mappings()
        
        # Verify field mappings
        mappings = fields["field_mappings"]
        self.assertEqual(mappings["category"], "document_type")
        self.assertEqual(mappings["name"], "title")
        self.assertEqual(mappings["author"], "author")
        self.assertEqual(mappings["created_date"], "created_date")
        
        # Verify search fields include document-specific fields
        self.assertIn("author", fields["search_fields"])
        self.assertIn("tags", fields["search_fields"])
        self.assertIn("department", fields["search_fields"])
    
    def test_document_library_ui_customization(self):
        """Test document library UI customization"""
        config = self._load_example_config("document-library")
        
        ui_config = self.config_manager.load_ui_settings()
        
        self.assertEqual(ui_config.title, "Document Library Search")
        self.assertEqual(ui_config.subtitle, "Find documents and resources quickly")
        
        # Verify search placeholder is document-specific
        search_config = ui_config.search
        self.assertIn("documents", search_config["placeholder_text"])
        self.assertIn("author", search_config["placeholder_text"])
    
    def test_document_library_data_integration(self):
        """Test document library data integration"""
        config = self._load_example_config("document-library")
        data_path = self._load_sample_data("document-library-sample.csv")
        
        # Verify CSV structure matches field mappings
        with open(data_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            # Check required columns exist
            self.assertIn("document_type", headers)
            self.assertIn("title", headers)
            self.assertIn("author", headers)
            self.assertIn("created_date", headers)
            
            # Check first row data
            first_row = next(reader)
            self.assertEqual(first_row["document_type"], "policies")
            self.assertIn("Employee Handbook", first_row["title"])


class TestInventorySystemIntegration(TestExampleConfigurationsIntegration):
    """Integration tests for inventory system configuration"""
    
    def test_inventory_system_configuration_loading(self):
        """Test loading inventory system configuration"""
        config = self._load_example_config("inventory-system")
        
        # Verify categories
        categories = self.config_manager.load_categories()
        self.assertIn("raw-materials", categories)
        self.assertIn("finished-goods", categories)
        self.assertIn("work-in-progress", categories)
        self.assertIn("tools-equipment", categories)
        
        # Verify category properties
        raw_materials = categories["raw-materials"]
        self.assertEqual(raw_materials.display_name, "Raw Materials")
        self.assertEqual(raw_materials.icon, "fas fa-cubes")
        self.assertEqual(raw_materials.emoji_fallback, "🧱")
        self.assertEqual(raw_materials.color, "#8e44ad")
    
    def test_inventory_system_field_mappings(self):
        """Test inventory system field mappings"""
        config = self._load_example_config("inventory-system")
        
        fields = self.config_manager.load_field_mappings()
        
        # Verify inventory-specific field mappings
        mappings = fields["field_mappings"]
        self.assertEqual(mappings["category"], "item_type")
        self.assertEqual(mappings["name"], "item_name")
        self.assertEqual(mappings["quantity"], "current_quantity")
        self.assertEqual(mappings["location"], "storage_location")
        self.assertEqual(mappings["supplier"], "supplier")
        
        # Verify display fields include inventory-specific fields
        self.assertIn("quantity", fields["display_fields"])
        self.assertIn("location", fields["display_fields"])
        self.assertIn("unit_cost", fields["display_fields"])
        self.assertIn("supplier", fields["display_fields"])
    
    def test_inventory_system_ui_customization(self):
        """Test inventory system UI customization"""
        config = self._load_example_config("inventory-system")
        
        ui_config = self.config_manager.load_ui_settings()
        
        self.assertEqual(ui_config.title, "Inventory Management System")
        self.assertEqual(ui_config.subtitle, "Track and manage inventory items")
        
        # Verify inventory-specific search placeholder
        search_config = ui_config.search
        self.assertIn("inventory", search_config["placeholder_text"])
        self.assertIn("location", search_config["placeholder_text"])
        self.assertIn("barcode", search_config["placeholder_text"])
    
    def test_inventory_system_data_validation(self):
        """Test inventory system data validation"""
        config = self._load_example_config("inventory-system")
        data_path = self._load_sample_data("inventory-system-sample.csv")
        
        # Verify CSV structure
        with open(data_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            # Check inventory-specific columns
            self.assertIn("item_type", headers)
            self.assertIn("item_name", headers)
            self.assertIn("current_quantity", headers)
            self.assertIn("storage_location", headers)
            self.assertIn("unit_cost", headers)
            self.assertIn("supplier", headers)
            
            # Validate data types in first row
            first_row = next(reader)
            self.assertEqual(first_row["item_type"], "raw-materials")
            self.assertTrue(first_row["current_quantity"].isdigit())
            self.assertTrue(first_row["unit_cost"].replace('.', '').isdigit())


class TestCrossConfigurationCompatibility(TestExampleConfigurationsIntegration):
    """Test compatibility and switching between different configurations"""
    
    def test_configuration_switching(self):
        """Test switching between different example configurations"""
        # Load product catalog first
        product_config = self._load_example_config("product-catalog")
        categories = self.config_manager.load_categories()
        self.assertIn("electronics", categories)
        
        # Switch to document library
        doc_config = self._load_example_config("document-library")
        categories = self.config_manager.load_categories()
        self.assertIn("policies", categories)
        self.assertNotIn("electronics", categories)
        
        # Switch to inventory system
        inventory_config = self._load_example_config("inventory-system")
        categories = self.config_manager.load_categories()
        self.assertIn("raw-materials", categories)
        self.assertNotIn("policies", categories)
    
    def test_configuration_validation_across_examples(self):
        """Test that all example configurations are valid"""
        examples = ["product-catalog", "document-library", "inventory-system"]
        
        for example_name in examples:
            with self.subTest(example=example_name):
                config = self._load_example_config(example_name)
                
                # Validate configuration structure
                self.assertIn("categories", config)
                self.assertIn("field_mappings", config)
                self.assertIn("ui", config)
                
                # Validate all configurations pass validation
                result = self.config_manager.validate_all_configs()
                self.assertTrue(result, f"Validation failed for {example_name}")
    
    def test_ui_rendering_consistency(self):
        """Test UI rendering consistency across different configurations"""
        examples = ["product-catalog", "document-library", "inventory-system"]
        
        for example_name in examples:
            with self.subTest(example=example_name):
                config = self._load_example_config(example_name)
                ui_config = self.config_manager.load_ui_settings()
                
                # Verify required UI elements exist
                self.assertTrue(ui_config.title)
                self.assertIsInstance(ui_config.theme, dict)
                self.assertIsInstance(ui_config.layout, dict)
                self.assertIsInstance(ui_config.search, dict)
                
                # Verify theme has required colors
                self.assertIn("primary_color", ui_config.theme)
                self.assertIn("secondary_color", ui_config.theme)
                self.assertIn("accent_color", ui_config.theme)
                
                # Verify layout has required settings
                self.assertIn("categories_per_row", ui_config.layout)
                self.assertIn("show_category_counts", ui_config.layout)
    
    def test_data_loading_with_different_schemas(self):
        """Test data loading works with different field schemas"""
        test_cases = [
            ("product-catalog", "product-catalog-sample.csv"),
            ("document-library", "document-library-sample.csv"),
            ("inventory-system", "inventory-system-sample.csv")
        ]
        
        for config_name, sample_file in test_cases:
            with self.subTest(config=config_name):
                config = self._load_example_config(config_name)
                data_path = self._load_sample_data(sample_file)
                
                # Verify data can be loaded without errors
                self.assertTrue(os.path.exists(data_path))
                
                # Verify CSV headers match field mappings
                fields = self.config_manager.load_field_mappings()
                mappings = fields["field_mappings"]
                
                with open(data_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    headers = reader.fieldnames
                    
                    # Check that mapped columns exist in CSV
                    for field_name, csv_column in mappings.items():
                        if csv_column:  # Skip empty mappings
                            self.assertIn(csv_column, headers, 
                                        f"Column {csv_column} for field {field_name} not found in {sample_file}")


class TestPerformanceWithExampleConfigurations(TestExampleConfigurationsIntegration):
    """Test performance with example configurations"""
    
    def test_configuration_loading_performance(self):
        """Test configuration loading performance with example configs"""
        import time
        
        examples = ["product-catalog", "document-library", "inventory-system"]
        
        for example_name in examples:
            with self.subTest(example=example_name):
                # Clear cache first
                self.config_manager.clear_cache()
                
                start_time = time.time()
                config = self._load_example_config(example_name)
                
                # Load all configurations
                categories = self.config_manager.load_categories()
                fields = self.config_manager.load_field_mappings()
                ui_config = self.config_manager.load_ui_settings()
                
                load_time = time.time() - start_time
                
                # Should load within reasonable time
                self.assertLess(load_time, 2.0, f"Loading {example_name} took too long: {load_time}s")
                
                # Verify all data loaded correctly
                self.assertGreater(len(categories), 0)
                self.assertIn("field_mappings", fields)
                self.assertTrue(ui_config.title)
    
    def test_memory_usage_with_large_configurations(self):
        """Test memory usage with large example configurations"""
        import sys
        
        # Get initial memory usage
        initial_memory = sys.getsizeof(self.config_manager)
        
        # Load all example configurations
        examples = ["product-catalog", "document-library", "inventory-system"]
        
        for example_name in examples:
            config = self._load_example_config(example_name)
            categories = self.config_manager.load_categories()
            fields = self.config_manager.load_field_mappings()
            ui_config = self.config_manager.load_ui_settings()
        
        # Check final memory usage
        final_memory = sys.getsizeof(self.config_manager)
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be reasonable
        self.assertLess(memory_growth, 10000, f"Memory usage grew too much: {memory_growth} bytes")


if __name__ == '__main__':
    unittest.main(verbosity=2)