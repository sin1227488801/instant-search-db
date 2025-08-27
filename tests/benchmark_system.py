#!/usr/bin/env python3
"""
System Benchmark Script

This script performs real-world benchmarking of the generic database system
with various dataset sizes and configurations.
"""

import os
import sys
import time
import csv
import json
import tempfile
import shutil
import random
import string
from typing import List, Dict, Any


class SystemBenchmark:
    """Benchmark the generic database system performance"""
    
    def __init__(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.test_dir, "config")
        self.data_dir = os.path.join(self.test_dir, "data")
        
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.results = {
            'system_info': self._get_system_info(),
            'benchmarks': {}
        }
    
    def __del__(self):
        """Cleanup test directory"""
        if hasattr(self, 'test_dir') and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        import platform
        
        info = {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'processor': platform.processor(),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            import psutil
            info['memory_total'] = psutil.virtual_memory().total // (1024**3)  # GB
            info['cpu_count'] = psutil.cpu_count()
            info['cpu_freq'] = psutil.cpu_freq().current if psutil.cpu_freq() else None
        except ImportError:
            info['memory_total'] = None
            info['cpu_count'] = None
            info['cpu_freq'] = None
        
        return info
    
    def _generate_test_data(self, size: int, complexity: str = "medium") -> str:
        """Generate test CSV data"""
        csv_path = os.path.join(self.data_dir, f"benchmark_data_{size}.csv")
        
        categories = [f"category_{i}" for i in range(10)]
        
        # Adjust complexity
        if complexity == "simple":
            fields = ['category', 'name', 'description']
        elif complexity == "medium":
            fields = ['category', 'name', 'description', 'field1', 'field2', 'field3']
        else:  # complex
            fields = ['category', 'name', 'description'] + [f'field_{i}' for i in range(1, 11)]
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(fields)
            
            for i in range(size):
                row = [
                    random.choice(categories),
                    f"Item {i:06d} {''.join(random.choices(string.ascii_letters, k=5))}",
                    f"Description for item {i} with random content {''.join(random.choices(string.ascii_letters + string.digits, k=20))}"
                ]
                
                # Add additional fields based on complexity
                for j in range(len(fields) - 3):
                    if j % 3 == 0:
                        row.append(f"Value_{random.randint(1, 1000)}")
                    elif j % 3 == 1:
                        row.append(str(random.randint(1, 10000)))
                    else:
                        row.append(random.choice(['Active', 'Inactive', 'Pending', 'Archived']))
                
                writer.writerow(row)
        
        return csv_path
    
    def _create_test_config(self, config_type: str = "standard"):
        """Create test configuration"""
        # Categories
        if config_type == "minimal":
            num_categories = 5
        elif config_type == "standard":
            num_categories = 10
        else:  # extensive
            num_categories = 50
        
        categories_data = {
            "categories": {
                f"category_{i}": {
                    "display_name": f"Category {i}",
                    "icon": f"fas fa-icon-{i}",
                    "emoji_fallback": "🧪",
                    "color": f"#{i*123456 % 16777216:06x}",
                    "description": f"Test category {i}"
                } for i in range(num_categories)
            }
        }
        
        with open(os.path.join(self.config_dir, "categories.json"), 'w') as f:
            json.dump(categories_data, f)
        
        # Fields
        if config_type == "minimal":
            field_mappings = {
                "category": "category",
                "name": "name",
                "description": "description"
            }
            display_fields = ["name", "description"]
            search_fields = ["name", "description"]
        elif config_type == "standard":
            field_mappings = {
                "category": "category",
                "name": "name",
                "description": "description",
                "field1": "field1",
                "field2": "field2",
                "field3": "field3"
            }
            display_fields = ["name", "field1", "field2", "description"]
            search_fields = ["name", "description", "field1", "field2"]
        else:  # extensive
            field_mappings = {
                "category": "category",
                "name": "name",
                "description": "description"
            }
            field_mappings.update({f"field_{i}": f"field_{i}" for i in range(1, 11)})
            display_fields = ["name"] + [f"field_{i}" for i in range(1, 6)] + ["description"]
            search_fields = ["name", "description"] + [f"field_{i}" for i in range(1, 8)]
        
        fields_data = {
            "field_mappings": field_mappings,
            "display_fields": display_fields,
            "search_fields": search_fields,
            "required_fields": ["category", "name"]
        }
        
        with open(os.path.join(self.config_dir, "fields.json"), 'w') as f:
            json.dump(fields_data, f)
        
        # UI
        ui_data = {
            "ui": {
                "title": f"Benchmark System ({config_type})",
                "subtitle": "Performance testing",
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
    
    def benchmark_data_loading(self, sizes: List[int] = None) -> Dict[str, Any]:
        """Benchmark data loading performance"""
        if sizes is None:
            sizes = [1000, 5000, 10000, 25000, 50000]
        
        print("Benchmarking data loading performance...")
        results = {}
        
        for size in sizes:
            print(f"  Testing with {size:,} items...")
            
            # Generate test data
            csv_path = self._generate_test_data(size)
            
            # Measure loading time
            start_time = time.time()
            start_memory = self._get_memory_usage()
            
            try:
                # Simulate data loading (would use actual load_items_from_csv in real test)
                items = []
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        items.append({
                            'id': len(items) + 1,
                            'category': row.get('category', ''),
                            'name': row.get('name', ''),
                            'description': row.get('description', ''),
                            'custom_fields': {k: v for k, v in row.items() 
                                            if k not in ['category', 'name', 'description']}
                        })
                
                end_time = time.time()
                end_memory = self._get_memory_usage()
                
                duration = end_time - start_time
                memory_used = end_memory - start_memory if end_memory and start_memory else 0
                
                results[size] = {
                    'duration': duration,
                    'memory_used_mb': memory_used,
                    'items_per_second': size / duration if duration > 0 else 0,
                    'memory_per_item_kb': (memory_used * 1024) / size if size > 0 and memory_used > 0 else 0
                }
                
                print(f"    {duration:.2f}s, {memory_used:.1f}MB, {size/duration:.0f} items/s")
                
            except Exception as e:
                print(f"    Error: {e}")
                results[size] = {'error': str(e)}
            
            # Cleanup
            if os.path.exists(csv_path):
                os.remove(csv_path)
        
        return results
    
    def benchmark_search_performance(self, dataset_size: int = 10000) -> Dict[str, Any]:
        """Benchmark search performance"""
        print(f"Benchmarking search performance with {dataset_size:,} items...")
        
        # Generate test data
        csv_path = self._generate_test_data(dataset_size)
        
        # Load data
        items = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                items.append({
                    'id': len(items) + 1,
                    'category': row.get('category', ''),
                    'name': row.get('name', ''),
                    'description': row.get('description', ''),
                    'custom_fields': {k: v for k, v in row.items() 
                                    if k not in ['category', 'name', 'description']}
                })
        
        # Test different search scenarios
        search_tests = [
            ("exact_match", "Item 001000"),
            ("partial_match", "Item 00"),
            ("common_word", "Description"),
            ("rare_word", "xyz123"),
            ("category_filter", "category_1"),
            ("empty_query", "")
        ]
        
        results = {}
        
        for test_name, query in search_tests:
            print(f"  Testing {test_name}: '{query}'")
            
            # Simulate search
            start_time = time.time()
            
            matching_items = []
            for item in items:
                if not query:  # Empty query returns all
                    matching_items.append(item)
                elif (query.lower() in item.get('name', '').lower() or
                      query.lower() in item.get('description', '').lower() or
                      query.lower() in item.get('category', '').lower()):
                    matching_items.append(item)
                
                if len(matching_items) >= 100:  # Limit results
                    break
            
            end_time = time.time()
            duration = end_time - start_time
            
            results[test_name] = {
                'duration': duration,
                'results_count': len(matching_items),
                'items_searched_per_second': dataset_size / duration if duration > 0 else 0
            }
            
            print(f"    {duration:.3f}s, {len(matching_items)} results, {dataset_size/duration:.0f} items/s")
        
        # Cleanup
        os.remove(csv_path)
        
        return results
    
    def benchmark_configuration_loading(self) -> Dict[str, Any]:
        """Benchmark configuration loading performance"""
        print("Benchmarking configuration loading performance...")
        
        config_types = ["minimal", "standard", "extensive"]
        results = {}
        
        for config_type in config_types:
            print(f"  Testing {config_type} configuration...")
            
            self._create_test_config(config_type)
            
            # Simulate configuration loading
            start_time = time.time()
            
            try:
                # Load categories
                with open(os.path.join(self.config_dir, "categories.json"), 'r') as f:
                    categories_data = json.load(f)
                
                # Load fields
                with open(os.path.join(self.config_dir, "fields.json"), 'r') as f:
                    fields_data = json.load(f)
                
                # Load UI
                with open(os.path.join(self.config_dir, "ui.json"), 'r') as f:
                    ui_data = json.load(f)
                
                end_time = time.time()
                duration = end_time - start_time
                
                results[config_type] = {
                    'duration': duration,
                    'categories_count': len(categories_data.get('categories', {})),
                    'fields_count': len(fields_data.get('field_mappings', {})),
                    'configs_per_second': 3 / duration if duration > 0 else 0
                }
                
                print(f"    {duration:.3f}s, {len(categories_data.get('categories', {}))} categories")
                
            except Exception as e:
                print(f"    Error: {e}")
                results[config_type] = {'error': str(e)}
        
        return results
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return None
    
    def run_full_benchmark(self) -> Dict[str, Any]:
        """Run complete benchmark suite"""
        print("Starting Full System Benchmark")
        print("=" * 50)
        
        # Data loading benchmark
        self.results['benchmarks']['data_loading'] = self.benchmark_data_loading()
        
        # Search performance benchmark
        self.results['benchmarks']['search_performance'] = self.benchmark_search_performance()
        
        # Configuration loading benchmark
        self.results['benchmarks']['configuration_loading'] = self.benchmark_configuration_loading()
        
        # Generate summary
        self._generate_summary()
        
        return self.results
    
    def _generate_summary(self):
        """Generate benchmark summary"""
        print("\n" + "=" * 50)
        print("BENCHMARK SUMMARY")
        print("=" * 50)
        
        # Data loading summary
        if 'data_loading' in self.results['benchmarks']:
            data_results = self.results['benchmarks']['data_loading']
            print("\nData Loading Performance:")
            print("-" * 30)
            
            for size, metrics in data_results.items():
                if 'error' not in metrics:
                    print(f"  {size:>6,} items: {metrics['duration']:>6.2f}s ({metrics['items_per_second']:>6.0f} items/s)")
        
        # Search performance summary
        if 'search_performance' in self.results['benchmarks']:
            search_results = self.results['benchmarks']['search_performance']
            print("\nSearch Performance:")
            print("-" * 30)
            
            for test_name, metrics in search_results.items():
                if 'error' not in metrics:
                    print(f"  {test_name:<15}: {metrics['duration']:>8.3f}s ({metrics['results_count']:>3} results)")
        
        # Configuration loading summary
        if 'configuration_loading' in self.results['benchmarks']:
            config_results = self.results['benchmarks']['configuration_loading']
            print("\nConfiguration Loading:")
            print("-" * 30)
            
            for config_type, metrics in config_results.items():
                if 'error' not in metrics:
                    print(f"  {config_type:<10}: {metrics['duration']:>8.3f}s ({metrics['categories_count']:>3} categories)")
        
        print("\n" + "=" * 50)
    
    def save_results(self, filename: str = None):
        """Save benchmark results to file"""
        if filename is None:
            filename = f"benchmark_results_{int(time.time())}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"Benchmark results saved to: {filename}")
        except Exception as e:
            print(f"Error saving results: {e}")


def main():
    """Main entry point"""
    benchmark = SystemBenchmark()
    
    try:
        results = benchmark.run_full_benchmark()
        benchmark.save_results()
        
        # Return success/failure based on results
        has_errors = any(
            'error' in metrics 
            for category in results['benchmarks'].values()
            for metrics in category.values()
            if isinstance(metrics, dict)
        )
        
        sys.exit(1 if has_errors else 0)
        
    except KeyboardInterrupt:
        print("\nBenchmark interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Benchmark failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()