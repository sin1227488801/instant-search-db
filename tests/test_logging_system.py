"""
Tests for the comprehensive logging system.
"""

import unittest
import tempfile
import os
import json
import time
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from instant_search_db.logging_system import (
    LoggingSystem, LogLevel, LogCategory, StructuredFormatter,
    performance_monitor, log_user_action, log_configuration_change,
    get_logging_system, initialize_logging
)


class TestStructuredFormatter(unittest.TestCase):
    """Test cases for StructuredFormatter"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.formatter = StructuredFormatter()
    
    def test_basic_formatting(self):
        """Test basic log record formatting"""
        import logging
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.module = "test_module"
        record.funcName = "test_function"
        
        formatted = self.formatter.format(record)
        log_data = json.loads(formatted)
        
        self.assertEqual(log_data["level"], "INFO")
        self.assertEqual(log_data["logger"], "test_logger")
        self.assertEqual(log_data["message"], "Test message")
        self.assertEqual(log_data["module"], "test_module")
        self.assertEqual(log_data["function"], "test_function")
        self.assertEqual(log_data["line"], 10)
    
    def test_extra_fields_formatting(self):
        """Test formatting with extra fields"""
        import logging
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.module = "test_module"
        record.funcName = "test_function"
        record.category = "test_category"
        record.user_id = "test_user"
        record.operation = "test_operation"
        record.duration = 1.5
        record.additional_data = {"key": "value"}
        
        formatted = self.formatter.format(record)
        log_data = json.loads(formatted)
        
        self.assertEqual(log_data["category"], "test_category")
        self.assertEqual(log_data["user_id"], "test_user")
        self.assertEqual(log_data["operation"], "test_operation")
        self.assertEqual(log_data["duration"], 1.5)
        self.assertEqual(log_data["additional_data"], {"key": "value"})


class TestLoggingSystem(unittest.TestCase):
    """Test cases for LoggingSystem class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.logging_system = LoggingSystem(
            log_dir=self.temp_dir,
            app_name="test_app",
            max_log_size=1024,  # Small size for testing
            backup_count=2
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test logging system initialization"""
        # Check that log directory was created
        self.assertTrue(os.path.exists(self.temp_dir))
        
        # Check that loggers were created
        self.assertIn('main', self.logging_system.loggers)
        self.assertIn('error', self.logging_system.loggers)
        self.assertIn('performance', self.logging_system.loggers)
        self.assertIn('config', self.logging_system.loggers)
        self.assertIn('validation', self.logging_system.loggers)
        self.assertIn('user', self.logging_system.loggers)
        self.assertIn('debug', self.logging_system.loggers)
    
    def test_get_logger_by_category(self):
        """Test getting loggers by category"""
        system_logger = self.logging_system.get_logger(LogCategory.SYSTEM)
        config_logger = self.logging_system.get_logger(LogCategory.CONFIGURATION)
        performance_logger = self.logging_system.get_logger(LogCategory.PERFORMANCE)
        
        self.assertIsNotNone(system_logger)
        self.assertIsNotNone(config_logger)
        self.assertIsNotNone(performance_logger)
        
        # Test that different categories return appropriate loggers
        self.assertEqual(system_logger, self.logging_system.loggers['main'])
        self.assertEqual(config_logger, self.logging_system.loggers['config'])
        self.assertEqual(performance_logger, self.logging_system.loggers['performance'])
    
    def test_performance_logging(self):
        """Test performance metric logging"""
        operation = "test_operation"
        duration = 2.5
        additional_data = {"items_processed": 100}
        
        self.logging_system.log_performance(
            operation=operation,
            duration=duration,
            category=LogCategory.DATA_MANAGEMENT,
            additional_data=additional_data,
            success=True
        )
        
        # Check that metric was stored
        self.assertEqual(len(self.logging_system.performance_metrics), 1)
        metric = self.logging_system.performance_metrics[0]
        
        self.assertEqual(metric.operation, operation)
        self.assertEqual(metric.duration, duration)
        self.assertEqual(metric.category, LogCategory.DATA_MANAGEMENT)
        self.assertEqual(metric.additional_data, additional_data)
        self.assertTrue(metric.success)
    
    def test_configuration_change_logging(self):
        """Test configuration change logging"""
        config_type = "categories"
        old_value = {"count": 5}
        new_value = {"count": 6}
        user = "admin"
        source = "api"
        
        self.logging_system.log_configuration_change(
            config_type=config_type,
            old_value=old_value,
            new_value=new_value,
            user=user,
            source=source
        )
        
        # Check that change was stored
        self.assertEqual(len(self.logging_system.config_changes), 1)
        change = self.logging_system.config_changes[0]
        
        self.assertEqual(change.config_type, config_type)
        self.assertEqual(change.old_value, old_value)
        self.assertEqual(change.new_value, new_value)
        self.assertEqual(change.user, user)
        self.assertEqual(change.source, source)
    
    def test_user_action_logging(self):
        """Test user action logging"""
        action = "search_performed"
        user_id = "user123"
        additional_data = {"query": "test", "results": 5}
        
        # This should not raise an exception
        self.logging_system.log_user_action(
            action=action,
            user_id=user_id,
            additional_data=additional_data
        )
        
        # We can't easily verify the log output without complex setup,
        # but we can ensure the method executes without error
        self.assertTrue(True)
    
    def test_data_validation_logging(self):
        """Test data validation logging"""
        validation_type = "csv_structure"
        result = True
        details = {"rows_validated": 100, "errors": 0}
        
        # This should not raise an exception
        self.logging_system.log_data_validation(
            validation_type=validation_type,
            result=result,
            details=details
        )
        
        self.assertTrue(True)
    
    def test_performance_summary(self):
        """Test performance summary generation"""
        # Add some test metrics
        operations = ["search", "load_data", "search", "validate"]
        durations = [0.1, 2.0, 0.15, 0.5]
        successes = [True, True, False, True]
        
        for op, dur, success in zip(operations, durations, successes):
            self.logging_system.log_performance(
                operation=op,
                duration=dur,
                success=success
            )
        
        summary = self.logging_system.get_performance_summary(24)
        
        self.assertEqual(summary["total_operations"], 4)
        self.assertEqual(summary["successful_operations"], 3)
        self.assertEqual(summary["failed_operations"], 1)
        self.assertEqual(summary["success_rate"], 0.75)
        
        # Check operation statistics
        self.assertIn("operation_statistics", summary)
        stats = summary["operation_statistics"]
        
        # Search operation should have 2 entries
        self.assertEqual(stats["search"]["count"], 2)
        self.assertEqual(stats["search"]["success_count"], 1)
        self.assertEqual(stats["search"]["success_rate"], 0.5)
        
        # Load_data operation should have 1 entry
        self.assertEqual(stats["load_data"]["count"], 1)
        self.assertEqual(stats["load_data"]["success_count"], 1)
        self.assertEqual(stats["load_data"]["success_rate"], 1.0)
    
    def test_configuration_history(self):
        """Test configuration change history"""
        # Add some test configuration changes
        changes = [
            ("categories", {"old": 1}, {"new": 1}),
            ("ui", {"old": 2}, {"new": 2}),
            ("categories", {"old": 3}, {"new": 3}),
        ]
        
        for config_type, old_val, new_val in changes:
            self.logging_system.log_configuration_change(
                config_type=config_type,
                old_value=old_val,
                new_value=new_val,
                user="test_user"
            )
        
        # Get all history
        all_history = self.logging_system.get_configuration_history(hours=24)
        self.assertEqual(len(all_history), 3)
        
        # Get filtered history
        categories_history = self.logging_system.get_configuration_history(
            config_type="categories", 
            hours=24
        )
        self.assertEqual(len(categories_history), 2)
        
        # Check that timestamps are ISO formatted strings
        for change in all_history:
            self.assertIsInstance(change["timestamp"], str)
            # Should be able to parse as ISO format
            datetime.fromisoformat(change["timestamp"])
    
    def test_metrics_cleanup(self):
        """Test that old metrics are cleaned up"""
        # Add more than 1000 metrics to trigger cleanup
        for i in range(1005):
            self.logging_system.log_performance(
                operation=f"operation_{i}",
                duration=0.1
            )
        
        # Should be limited to 1000
        self.assertEqual(len(self.logging_system.performance_metrics), 1000)
    
    def test_config_changes_cleanup(self):
        """Test that old configuration changes are cleaned up"""
        # Add more than 500 changes to trigger cleanup
        for i in range(505):
            self.logging_system.log_configuration_change(
                config_type=f"config_{i}",
                old_value=i,
                new_value=i+1
            )
        
        # Should be limited to 500
        self.assertEqual(len(self.logging_system.config_changes), 500)


class TestPerformanceMonitorDecorator(unittest.TestCase):
    """Test cases for performance monitor decorator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.logging_system = LoggingSystem(log_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_successful_operation_monitoring(self):
        """Test monitoring of successful operations"""
        
        @performance_monitor("test_operation", LogCategory.SYSTEM, log_args=True)
        def test_function(x, y, z=None):
            time.sleep(0.01)  # Small delay to measure
            return x + y
        
        result = test_function(1, 2, z="test")
        
        self.assertEqual(result, 3)
        
        # Check that performance was logged
        metrics = [m for m in self.logging_system.performance_metrics 
                  if m.operation == "test_operation"]
        
        self.assertEqual(len(metrics), 1)
        metric = metrics[0]
        
        self.assertTrue(metric.success)
        self.assertGreater(metric.duration, 0)
        self.assertEqual(metric.additional_data["args_count"], 2)
        self.assertEqual(metric.additional_data["kwargs_keys"], ["z"])
    
    def test_failed_operation_monitoring(self):
        """Test monitoring of failed operations"""
        
        @performance_monitor("failing_operation")
        def failing_function():
            raise ValueError("Test error")
        
        with self.assertRaises(ValueError):
            failing_function()
        
        # Check that performance was logged with failure
        metrics = [m for m in self.logging_system.performance_metrics 
                  if m.operation == "failing_operation"]
        
        self.assertEqual(len(metrics), 1)
        metric = metrics[0]
        
        self.assertFalse(metric.success)
        self.assertIn("error", metric.additional_data)
        self.assertEqual(metric.additional_data["error"], "Test error")


class TestGlobalFunctions(unittest.TestCase):
    """Test cases for global convenience functions"""
    
    def test_get_logging_system(self):
        """Test global logging system getter"""
        system1 = get_logging_system()
        system2 = get_logging_system()
        
        # Should return the same instance
        self.assertIs(system1, system2)
    
    def test_initialize_logging(self):
        """Test logging system initialization"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            system = initialize_logging(
                log_dir=temp_dir,
                app_name="test_init",
                max_log_size=2048,
                backup_count=3
            )
            
            self.assertIsInstance(system, LoggingSystem)
            self.assertEqual(system.app_name, "test_init")
            self.assertEqual(system.max_log_size, 2048)
            self.assertEqual(system.backup_count, 3)
            
            # Should create log directory
            self.assertTrue(os.path.exists(temp_dir))
            
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_convenience_functions(self):
        """Test convenience functions for logging"""
        # These should not raise exceptions
        log_user_action("test_action", "user123", {"data": "test"})
        log_configuration_change("test_config", "old", "new", "admin", "api")
        
        # Verify they were logged in the global system
        global_system = get_logging_system()
        self.assertTrue(len(global_system.config_changes) > 0)


if __name__ == '__main__':
    unittest.main()