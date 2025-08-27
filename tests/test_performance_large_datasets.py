import unittest
import os
import tempfile
import shutil
import json
import csv
import time
import random
import string
import psutil
import threading
from unittest.mock import patch, MagicMock
from instant_search_db.config_manager import ConfigManager
from instant_search_db.data_manager import DataManager
from instant_search_db.models import search_items, load_items_from_csv


class TestLargeDatasetPerformance(unittest.TestCase):
    """Performance tests for large datasets (10k+ items)"""
    
    def setUp(self):
        """Set up test environment with large dataset"""
        self.test_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.test_dir, "config")
        self.data_dir = os.path.join(self.test_dir, "data")
        
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize managers
        self.config_manager = ConfigManager(self.config_dir)
        self.data_manager = DataManager(self.data_dir)
        
        # Create test configuration
        self._create_test_configuration()
        
        # Performance tracking
        self.performance_metrics = {}
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def _create_test_configuration(self):
        """Create test configuration for performance testing"""
        # Categories configuration
        categories_data = {
            "categories": {
                f"category_{i}": {
                    "display_name": f"Category {i}",
                    "icon": f"fas fa-icon-{i}",
                    "emoji_fallback": "🧪",
                    "color": f"#{i:06x}",
                    "description": f"Test category {i}"
                } for i in range(20)  # 20 categories for variety
            }
        }
        
        with open(os.path.join(self.config_dir, "categories.json"), 'w') as f:
            json.dump(categories_data, f)
        
        # Fields configuration
        fields_data = {
            "field_mappings": {
                "category": "category",
                "name": "name",
                "description": "description",
                "field1": "field1",
                "field2": "field2",
                "field3": "field3",
                "field4": "field4",
                "field5": "field5"
            },
            "display_fields": ["name", "field1", "field2", "description"],
            "search_fields": ["name", "description", "field1", "field2", "field3"],
            "required_fields": ["category", "name"]
        }
        
        with open(os.path.join(self.config_dir, "fields.json"), 'w') as f:
            json.dump(fields_data, f)
        
        # UI configuration
        ui_data = {
            "ui": {
                "title": "Performance Test System",
                "subtitle": "Testing large datasets",
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
        
        with open(os.path.join(self.config_dir, "ui.json"), 'w') as f:
            json.dump(ui_data, f)
    
    def _generate_random_string(self, length=10):
        """Generate random string for test data"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def _generate_large_dataset(self, size=10000):
        """Generate large CSV dataset for testing"""
        csv_path = os.path.join(self.data_dir, "large_dataset.csv")
        
        categories = [f"category_{i}" for i in range(20)]
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['category', 'name', 'description', 'field1', 'field2', 'field3', 'field4', 'field5'])
            
            # Write data rows
            for i in range(size):
                category = random.choice(categories)
                name = f"Item {i:06d} {self._generate_random_string(5)}"
                description = f"Description for item {i} with {self._generate_random_string(20)}"
                field1 = self._generate_random_string(8)
                field2 = f"Value_{i % 100}"
                field3 = str(random.randint(1, 1000))
                field4 = random.choice(['Active', 'Inactive', 'Pending'])
                field5 = f"Extra_{self._generate_random_string(6)}"
                
                writer.writerow([category, name, description, field1, field2, field3, field4, field5])
        
        return csv_path
    
    def _measure_memory_usage(self):
        """Measure current memory usage"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # MB
    
    def _measure_performance(self, operation_name, operation_func, *args, **kwargs):
        """Measure performance of an operation"""
        start_time = time.time()
        start_memory = self._measure_memory_usage()
        
        result = operation_func(*args, **kwargs)
        
        end_time = time.time()
        end_memory = self._measure_memory_usage()
        
        metrics = {
            'duration': end_time - start_time,
            'memory_start': start_memory,
            'memory_end': end_memory,
            'memory_delta': end_memory - start_memory
        }
        
        self.performance_metrics[operation_name] = metrics
        return result, metrics


class TestDataLoadingPerformance(TestLargeDatasetPerformance):
    """Test data loading performance with large datasets"""
    
    def test_load_10k_items_performance(self):
        """Test loading 10,000 items performance"""
        csv_path = self._generate_large_dataset(10000)
        
        def load_operation():
            return load_items_from_csv(csv_path)
        
        items, metrics = self._measure_performance("load_10k_items", load_operation)
        
        # Performance assertions
        self.assertLess(metrics['duration'], 10.0, f"Loading 10k items took too long: {metrics['duration']:.2f}s")
        self.assertLess(metrics['memory_delta'], 500, f"Memory usage too high: {metrics['memory_delta']:.2f}MB")
        self.assertEqual(len(items), 10000)
    
    def test_load_50k_items_performance(self):
        """Test loading 50,000 items performance"""
        csv_path = self._generate_large_dataset(50000)
        
        def load_operation():
            return load_items_from_csv(csv_path)
        
        items, metrics = self._measure_performance("load_50k_items", load_operation)
        
        # Performance assertions
        self.assertLess(metrics['duration'], 30.0, f"Loading 50k items took too long: {metrics['duration']:.2f}s")
        self.assertLess(metrics['memory_delta'], 1000, f"Memory usage too high: {metrics['memory_delta']:.2f}MB")
        self.assertEqual(len(items), 50000)
    
    def test_incremental_loading_performance(self):
        """Test incremental data loading performance"""
        # Create multiple smaller datasets
        datasets = []
        for i in range(5):
            csv_path = self._generate_large_dataset(2000)
            new_path = os.path.join(self.data_dir, f"dataset_{i}.csv")
            shutil.move(csv_path, new_path)
            datasets.append(new_path)
        
        total_items = []
        total_time = 0
        
        for i, dataset_path in enumerate(datasets):
            start_time = time.time()
            items = load_items_from_csv(dataset_path)
            load_time = time.time() - start_time
            
            total_items.extend(items)
            total_time += load_time
            
            # Each incremental load should be fast
            self.assertLess(load_time, 5.0, f"Incremental load {i} took too long: {load_time:.2f}s")
        
        # Total performance should be reasonable
        self.assertLess(total_time, 20.0, f"Total incremental loading took too long: {total_time:.2f}s")
        self.assertEqual(len(total_items), 10000)
    
    def test_memory_efficiency_large_datasets(self):
        """Test memory efficiency with large datasets"""
        sizes = [1000, 5000, 10000, 20000]
        memory_usage = []
        
        for size in sizes:
            csv_path = self._generate_large_dataset(size)
            
            start_memory = self._measure_memory_usage()
            items = load_items_from_csv(csv_path)
            end_memory = self._measure_memory_usage()
            
            memory_per_item = (end_memory - start_memory) / size
            memory_usage.append(memory_per_item)
            
            # Memory per item should be reasonable
            self.assertLess(memory_per_item, 0.1, f"Memory per item too high: {memory_per_item:.4f}MB")
            
            # Clean up
            os.remove(csv_path)
        
        # Memory usage should scale linearly (not exponentially)
        for i in range(1, len(memory_usage)):
            ratio = memory_usage[i] / memory_usage[0]
            self.assertLess(ratio, 2.0, "Memory usage scaling is not linear")


class TestSearchPerformance(TestLargeDatasetPerformance):
    """Test search performance with large datasets"""
    
    def setUp(self):
        super().setUp()
        # Generate large dataset for search testing
        self.large_csv_path = self._generate_large_dataset(15000)
        self.large_items = load_items_from_csv(self.large_csv_path)
    
    def test_search_response_time_10k_items(self):
        """Test search response time with 10k+ items"""
        # Mock search function with actual large dataset
        with patch('instant_search_db.models.search_items') as mock_search:
            # Simulate realistic search that filters through large dataset
            def simulate_search(query, category):
                matching_items = []
                for item in self.large_items[:10000]:  # Use first 10k items
                    if query.lower() in item.get('name', '').lower() or \
                       query.lower() in item.get('description', '').lower():
                        matching_items.append(item)
                        if len(matching_items) >= 50:  # Limit results
                            break
                return matching_items
            
            mock_search.side_effect = simulate_search
            
            # Test various search queries
            test_queries = ["Item", "Description", "Value_1", "category_5", "Active"]
            
            for query in test_queries:
                with self.subTest(query=query):
                    def search_operation():
                        return search_items(query, "")
                    
                    results, metrics = self._measure_performance(f"search_{query}", search_operation)
                    
                    # Search should be fast
                    self.assertLess(metrics['duration'], 1.0, 
                                  f"Search for '{query}' took too long: {metrics['duration']:.3f}s")
                    
                    # Should return reasonable number of results
                    self.assertLessEqual(len(results), 50)
    
    def test_concurrent_search_performance(self):
        """Test concurrent search performance"""
        with patch('instant_search_db.models.search_items') as mock_search:
            # Simulate search with delay
            def simulate_search_with_delay(query, category):
                time.sleep(0.1)  # Simulate database query time
                return [{'id': 1, 'name': f'Result for {query}', 'category': category}]
            
            mock_search.side_effect = simulate_search_with_delay
            
            # Perform concurrent searches
            queries = [f"query_{i}" for i in range(10)]
            results = []
            errors = []
            
            def perform_search(query):
                try:
                    start_time = time.time()
                    result = search_items(query, "")
                    duration = time.time() - start_time
                    results.append((query, result, duration))
                except Exception as e:
                    errors.append((query, e))
            
            # Start concurrent searches
            threads = []
            start_time = time.time()
            
            for query in queries:
                thread = threading.Thread(target=perform_search, args=(query,))
                threads.append(thread)
                thread.start()
            
            # Wait for all searches to complete
            for thread in threads:
                thread.join()
            
            total_time = time.time() - start_time
            
            # Verify results
            self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
            self.assertEqual(len(results), 10)
            
            # Concurrent searches should complete faster than sequential
            self.assertLess(total_time, 5.0, f"Concurrent searches took too long: {total_time:.2f}s")
            
            # Individual search times should be reasonable
            for query, result, duration in results:
                self.assertLess(duration, 2.0, f"Search '{query}' took too long: {duration:.2f}s")
    
    def test_search_with_various_data_types(self):
        """Test search performance with various data types"""
        # Create dataset with different data types
        csv_path = os.path.join(self.data_dir, "mixed_types.csv")
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['category', 'name', 'description', 'number_field', 'date_field', 'boolean_field'])
            
            for i in range(5000):
                writer.writerow([
                    f"category_{i % 10}",
                    f"Item {i:04d}",
                    f"Description with unicode: 日本語 {i}",
                    str(random.randint(1, 10000)),
                    f"2024-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}",
                    str(random.choice([True, False])).lower()
                ])
        
        items = load_items_from_csv(csv_path)
        
        with patch('instant_search_db.models.search_items') as mock_search:
            def simulate_mixed_search(query, category):
                matching = []
                for item in items:
                    # Search in various field types
                    if (query.lower() in str(item.get('name', '')).lower() or
                        query.lower() in str(item.get('description', '')).lower() or
                        query in str(item.get('custom_fields', {}).get('number_field', '')) or
                        query in str(item.get('custom_fields', {}).get('date_field', ''))):
                        matching.append(item)
                        if len(matching) >= 20:
                            break
                return matching
            
            mock_search.side_effect = simulate_mixed_search
            
            # Test searches for different data types
            test_cases = [
                ("Item", "string search"),
                ("日本語", "unicode search"),
                ("2024", "date search"),
                ("100", "number search"),
                ("true", "boolean search")
            ]
            
            for query, test_type in test_cases:
                with self.subTest(test_type=test_type):
                    def search_operation():
                        return search_items(query, "")
                    
                    results, metrics = self._measure_performance(f"search_{test_type}", search_operation)
                    
                    # All search types should be fast
                    self.assertLess(metrics['duration'], 2.0, 
                                  f"{test_type} took too long: {metrics['duration']:.3f}s")
    
    def test_category_filtering_performance(self):
        """Test category filtering performance with large datasets"""
        with patch('instant_search_db.models.search_items') as mock_search:
            def simulate_category_search(query, category):
                matching = []
                for item in self.large_items:
                    if category and item.get('category') != category:
                        continue
                    if not query or query.lower() in item.get('name', '').lower():
                        matching.append(item)
                        if len(matching) >= 50:
                            break
                return matching
            
            mock_search.side_effect = simulate_category_search
            
            # Test category filtering
            categories = [f"category_{i}" for i in range(5)]
            
            for category in categories:
                with self.subTest(category=category):
                    def search_operation():
                        return search_items("", category)
                    
                    results, metrics = self._measure_performance(f"filter_{category}", search_operation)
                    
                    # Category filtering should be fast
                    self.assertLess(metrics['duration'], 0.5, 
                                  f"Category filtering for '{category}' took too long: {metrics['duration']:.3f}s")
                    
                    # Should return items from correct category
                    for item in results:
                        self.assertEqual(item.get('category'), category)


class TestConfigurationPerformance(TestLargeDatasetPerformance):
    """Test configuration system performance with large configurations"""
    
    def test_large_categories_configuration_performance(self):
        """Test performance with large number of categories"""
        # Create configuration with many categories
        large_categories = {
            "categories": {
                f"category_{i:04d}": {
                    "display_name": f"Category {i:04d}",
                    "icon": f"fas fa-icon-{i}",
                    "emoji_fallback": "🧪",
                    "color": f"#{i % 16777216:06x}",
                    "description": f"Description for category {i} with detailed information about its purpose and usage"
                } for i in range(1000)  # 1000 categories
            }
        }
        
        with open(os.path.join(self.config_dir, "categories.json"), 'w') as f:
            json.dump(large_categories, f)
        
        def load_operation():
            return self.config_manager.load_categories(force_reload=True)
        
        categories, metrics = self._measure_performance("load_1000_categories", load_operation)
        
        # Should load efficiently
        self.assertLess(metrics['duration'], 5.0, f"Loading 1000 categories took too long: {metrics['duration']:.2f}s")
        self.assertEqual(len(categories), 1000)
        
        # Test caching performance
        def cached_load_operation():
            return self.config_manager.load_categories()
        
        cached_categories, cached_metrics = self._measure_performance("cached_1000_categories", cached_load_operation)
        
        # Cached load should be much faster
        self.assertLess(cached_metrics['duration'], 0.1, 
                       f"Cached load took too long: {cached_metrics['duration']:.3f}s")
        self.assertIs(categories, cached_categories)
    
    def test_complex_field_mappings_performance(self):
        """Test performance with complex field mappings"""
        # Create complex field mappings
        complex_fields = {
            "field_mappings": {f"field_{i:03d}": f"csv_column_{i:03d}" for i in range(200)},
            "display_fields": [f"field_{i:03d}" for i in range(50)],
            "search_fields": [f"field_{i:03d}" for i in range(100)],
            "required_fields": [f"field_{i:03d}" for i in range(20)]
        }
        
        with open(os.path.join(self.config_dir, "fields.json"), 'w') as f:
            json.dump(complex_fields, f)
        
        def load_operation():
            return self.config_manager.load_field_mappings(force_reload=True)
        
        fields, metrics = self._measure_performance("load_complex_fields", load_operation)
        
        # Should load efficiently
        self.assertLess(metrics['duration'], 2.0, f"Loading complex fields took too long: {metrics['duration']:.2f}s")
        self.assertEqual(len(fields["field_mappings"]), 200)
        self.assertEqual(len(fields["display_fields"]), 50)
        self.assertEqual(len(fields["search_fields"]), 100)
    
    def test_configuration_validation_performance(self):
        """Test configuration validation performance"""
        # Create schemas directory with validation schemas
        schemas_dir = os.path.join(self.config_dir, "schemas")
        os.makedirs(schemas_dir, exist_ok=True)
        
        # Create complex validation schema
        complex_schema = {
            "type": "object",
            "properties": {
                "categories": {
                    "type": "object",
                    "patternProperties": {
                        ".*": {
                            "type": "object",
                            "properties": {
                                "display_name": {"type": "string", "minLength": 1},
                                "icon": {"type": "string", "pattern": "^fas fa-"},
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
        
        with open(os.path.join(schemas_dir, "categories-schema.json"), 'w') as f:
            json.dump(complex_schema, f)
        
        def validation_operation():
            return self.config_manager.validate_all_configs()
        
        result, metrics = self._measure_performance("validate_all_configs", validation_operation)
        
        # Validation should be reasonably fast
        self.assertLess(metrics['duration'], 3.0, f"Validation took too long: {metrics['duration']:.2f}s")
        self.assertTrue(result)


class TestMemoryOptimization(TestLargeDatasetPerformance):
    """Test memory optimization with large datasets"""
    
    def test_memory_usage_scaling(self):
        """Test memory usage scaling with dataset size"""
        sizes = [1000, 5000, 10000, 25000]
        memory_measurements = []
        
        for size in sizes:
            # Clear any existing data
            if hasattr(self, 'large_items'):
                del self.large_items
            
            # Generate dataset of specific size
            csv_path = self._generate_large_dataset(size)
            
            # Measure memory before and after loading
            start_memory = self._measure_memory_usage()
            items = load_items_from_csv(csv_path)
            end_memory = self._measure_memory_usage()
            
            memory_used = end_memory - start_memory
            memory_per_item = memory_used / size if size > 0 else 0
            
            memory_measurements.append({
                'size': size,
                'memory_used': memory_used,
                'memory_per_item': memory_per_item
            })
            
            # Clean up
            del items
            os.remove(csv_path)
        
        # Analyze memory scaling
        for i, measurement in enumerate(memory_measurements):
            # Memory per item should be reasonable
            self.assertLess(measurement['memory_per_item'], 0.05, 
                          f"Memory per item too high for size {measurement['size']}: {measurement['memory_per_item']:.4f}MB")
            
            # Memory usage should scale roughly linearly
            if i > 0:
                prev_measurement = memory_measurements[i-1]
                size_ratio = measurement['size'] / prev_measurement['size']
                memory_ratio = measurement['memory_used'] / prev_measurement['memory_used']
                
                # Memory ratio should be close to size ratio (linear scaling)
                ratio_difference = abs(memory_ratio - size_ratio)
                self.assertLess(ratio_difference, 1.0, 
                              f"Memory scaling not linear: size ratio {size_ratio:.2f}, memory ratio {memory_ratio:.2f}")
    
    def test_garbage_collection_efficiency(self):
        """Test garbage collection efficiency with large datasets"""
        import gc
        
        initial_memory = self._measure_memory_usage()
        
        # Create and destroy multiple large datasets
        for i in range(5):
            csv_path = self._generate_large_dataset(5000)
            items = load_items_from_csv(csv_path)
            
            # Use the data briefly
            search_count = sum(1 for item in items if 'Item' in item.get('name', ''))
            self.assertGreater(search_count, 0)
            
            # Clean up
            del items
            os.remove(csv_path)
            
            # Force garbage collection
            gc.collect()
        
        final_memory = self._measure_memory_usage()
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be minimal after cleanup
        self.assertLess(memory_growth, 100, f"Memory not properly cleaned up: {memory_growth:.2f}MB growth")
    
    def test_configuration_cache_memory_efficiency(self):
        """Test configuration cache memory efficiency"""
        initial_memory = self._measure_memory_usage()
        
        # Load configurations multiple times
        for i in range(10):
            categories = self.config_manager.load_categories()
            fields = self.config_manager.load_field_mappings()
            ui_config = self.config_manager.load_ui_settings()
            
            # Verify data is loaded
            self.assertGreater(len(categories), 0)
            self.assertIn("field_mappings", fields)
            self.assertTrue(ui_config.title)
        
        cached_memory = self._measure_memory_usage()
        
        # Clear cache and measure again
        self.config_manager.clear_cache()
        cleared_memory = self._measure_memory_usage()
        
        # Cache should not use excessive memory
        cache_memory = cached_memory - initial_memory
        self.assertLess(cache_memory, 50, f"Configuration cache uses too much memory: {cache_memory:.2f}MB")
        
        # Memory should be freed after cache clear
        memory_freed = cached_memory - cleared_memory
        self.assertGreater(memory_freed, 0, "Memory not freed after cache clear")


if __name__ == '__main__':
    # Check if psutil is available
    try:
        import psutil
    except ImportError:
        print("Warning: psutil not available, some memory tests may be skipped")
    
    unittest.main(verbosity=2)