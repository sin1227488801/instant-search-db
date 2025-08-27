#!/usr/bin/env python3
"""
Performance Test Runner for Generic Database Enhancement

This script runs comprehensive performance tests and generates a performance report.
"""

import unittest
import sys
import time
import json
import os
from io import StringIO


class PerformanceTestResult(unittest.TestResult):
    """Custom test result class to capture performance metrics"""
    
    def __init__(self):
        super().__init__()
        self.performance_data = {}
        self.test_times = {}
        self.start_time = None
    
    def startTest(self, test):
        super().startTest(test)
        self.start_time = time.time()
    
    def stopTest(self, test):
        super().stopTest(test)
        if self.start_time:
            duration = time.time() - self.start_time
            test_name = f"{test.__class__.__name__}.{test._testMethodName}"
            self.test_times[test_name] = duration
            
            # Capture performance metrics if available
            if hasattr(test, 'performance_metrics'):
                self.performance_data[test_name] = test.performance_metrics


class PerformanceTestRunner:
    """Runner for performance tests with reporting"""
    
    def __init__(self):
        self.results = PerformanceTestResult()
        self.report_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'system_info': self._get_system_info(),
            'test_results': {},
            'summary': {}
        }
    
    def _get_system_info(self):
        """Get system information for the report"""
        import platform
        
        info = {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'processor': platform.processor(),
        }
        
        try:
            import psutil
            info['memory_total'] = f"{psutil.virtual_memory().total / (1024**3):.1f} GB"
            info['cpu_count'] = psutil.cpu_count()
        except ImportError:
            info['memory_total'] = 'Unknown'
            info['cpu_count'] = 'Unknown'
        
        return info
    
    def run_performance_tests(self):
        """Run all performance tests"""
        print("Starting Performance Test Suite...")
        print("=" * 60)
        
        # Import test modules
        try:
            from test_config_manager import TestConfigManager, TestConfigManagerErrorHandling, TestConfigManagerValidation, TestConfigManagerPerformance
            from test_integration_examples import TestExampleConfigurationsIntegration, TestProductCatalogIntegration, TestDocumentLibraryIntegration, TestInventorySystemIntegration, TestCrossConfigurationCompatibility, TestPerformanceWithExampleConfigurations
            from test_performance_large_datasets import TestLargeDatasetPerformance, TestDataLoadingPerformance, TestSearchPerformance, TestConfigurationPerformance, TestMemoryOptimization
        except ImportError as e:
            print(f"Warning: Could not import all test modules: {e}")
            return False
        
        # Create test suite
        suite = unittest.TestSuite()
        
        # Add configuration tests
        config_tests = [
            TestConfigManager,
            TestConfigManagerErrorHandling,
            TestConfigManagerValidation,
            TestConfigManagerPerformance
        ]
        
        for test_class in config_tests:
            tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
            suite.addTests(tests)
        
        # Add integration tests
        integration_tests = [
            TestProductCatalogIntegration,
            TestDocumentLibraryIntegration,
            TestInventorySystemIntegration,
            TestCrossConfigurationCompatibility,
            TestPerformanceWithExampleConfigurations
        ]
        
        for test_class in integration_tests:
            tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
            suite.addTests(tests)
        
        # Add performance tests
        performance_tests = [
            TestDataLoadingPerformance,
            TestSearchPerformance,
            TestConfigurationPerformance,
            TestMemoryOptimization
        ]
        
        for test_class in performance_tests:
            tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
            suite.addTests(tests)
        
        # Run tests
        start_time = time.time()
        suite.run(self.results)
        total_time = time.time() - start_time
        
        # Generate report
        self._generate_report(total_time)
        
        return self.results.wasSuccessful()
    
    def _generate_report(self, total_time):
        """Generate performance report"""
        self.report_data['summary'] = {
            'total_tests': self.results.testsRun,
            'failures': len(self.results.failures),
            'errors': len(self.results.errors),
            'skipped': len(self.results.skipped),
            'total_time': f"{total_time:.2f}s",
            'success_rate': f"{((self.results.testsRun - len(self.results.failures) - len(self.results.errors)) / self.results.testsRun * 100):.1f}%" if self.results.testsRun > 0 else "0%"
        }
        
        # Add test timing data
        self.report_data['test_times'] = self.results.test_times
        
        # Add performance metrics
        self.report_data['performance_metrics'] = self.results.performance_data
        
        # Print summary
        self._print_summary()
        
        # Save detailed report
        self._save_report()
    
    def _print_summary(self):
        """Print performance test summary"""
        print("\n" + "=" * 60)
        print("PERFORMANCE TEST SUMMARY")
        print("=" * 60)
        
        summary = self.report_data['summary']
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Failures: {summary['failures']}")
        print(f"Errors: {summary['errors']}")
        print(f"Skipped: {summary['skipped']}")
        print(f"Success Rate: {summary['success_rate']}")
        print(f"Total Time: {summary['total_time']}")
        
        print("\nSLOWEST TESTS:")
        print("-" * 40)
        
        # Sort tests by duration
        sorted_tests = sorted(self.results.test_times.items(), key=lambda x: x[1], reverse=True)
        
        for test_name, duration in sorted_tests[:10]:  # Top 10 slowest
            print(f"{test_name:<50} {duration:>8.3f}s")
        
        # Performance metrics summary
        if self.results.performance_data:
            print("\nPERFORMANCE METRICS:")
            print("-" * 40)
            
            for test_name, metrics in self.results.performance_data.items():
                if metrics:
                    print(f"\n{test_name}:")
                    for metric_name, metric_data in metrics.items():
                        if isinstance(metric_data, dict) and 'duration' in metric_data:
                            print(f"  {metric_name}: {metric_data['duration']:.3f}s")
                            if 'memory_delta' in metric_data:
                                print(f"    Memory: {metric_data['memory_delta']:.1f}MB")
        
        print("\n" + "=" * 60)
    
    def _save_report(self):
        """Save detailed performance report to file"""
        report_file = f"performance_report_{int(time.time())}.json"
        
        try:
            with open(report_file, 'w') as f:
                json.dump(self.report_data, f, indent=2)
            print(f"Detailed report saved to: {report_file}")
        except Exception as e:
            print(f"Warning: Could not save report file: {e}")
    
    def run_specific_test_category(self, category):
        """Run specific category of tests"""
        print(f"Running {category} tests...")
        
        if category == "config":
            from test_config_manager import TestConfigManager
            suite = unittest.TestLoader().loadTestsFromTestCase(TestConfigManager)
        elif category == "integration":
            from test_integration_examples import TestProductCatalogIntegration
            suite = unittest.TestLoader().loadTestsFromTestCase(TestProductCatalogIntegration)
        elif category == "performance":
            from test_performance_large_datasets import TestDataLoadingPerformance
            suite = unittest.TestLoader().loadTestsFromTestCase(TestDataLoadingPerformance)
        else:
            print(f"Unknown test category: {category}")
            return False
        
        start_time = time.time()
        suite.run(self.results)
        total_time = time.time() - start_time
        
        self._generate_report(total_time)
        return self.results.wasSuccessful()


def main():
    """Main entry point"""
    runner = PerformanceTestRunner()
    
    if len(sys.argv) > 1:
        category = sys.argv[1]
        success = runner.run_specific_test_category(category)
    else:
        success = runner.run_performance_tests()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()