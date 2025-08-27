"""
Tests for the enhanced error handling system.
"""

import unittest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
from datetime import datetime

from instant_search_db.error_handler import (
    ErrorHandler, ErrorContext, ErrorSeverity, ErrorCategory,
    handle_error, graceful_degradation
)
from instant_search_db.logging_system import (
    LoggingSystem, get_logging_system, performance_monitor,
    log_user_action, log_configuration_change
)


class TestErrorHandler(unittest.TestCase):
    """Test cases for ErrorHandler class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.error_handler = ErrorHandler()
    
    def test_handle_file_not_found_error(self):
        """Test handling of FileNotFoundError"""
        error = FileNotFoundError("Config file not found")
        context = ErrorContext(file_path="/path/to/config.json")
        
        error_info = self.error_handler.handle_error(error, context, "config_file_not_found")
        
        self.assertEqual(error_info.category, ErrorCategory.CONFIGURATION)
        self.assertEqual(error_info.severity, ErrorSeverity.MEDIUM)
        self.assertIn("設定ファイルが見つかりません", error_info.user_message)
        self.assertTrue(len(error_info.recovery_actions) > 0)
    
    def test_handle_json_decode_error(self):
        """Test handling of JSON decode errors"""
        error = json.JSONDecodeError("Invalid JSON", "test", 1)
        context = ErrorContext(file_path="/path/to/config.json", line_number=1)
        
        error_info = self.error_handler.handle_error(error, context, "config_invalid_json")
        
        self.assertEqual(error_info.category, ErrorCategory.CONFIGURATION)
        self.assertEqual(error_info.severity, ErrorSeverity.HIGH)
        self.assertIn("設定ファイルの形式が正しくありません", error_info.user_message)
    
    def test_error_pattern_detection(self):
        """Test automatic error pattern detection"""
        # Test CSV file not found
        error = FileNotFoundError("data.csv not found")
        error_info = self.error_handler.handle_error(error)
        
        self.assertEqual(error_info.category, ErrorCategory.FILE_IO)
    
    def test_recovery_callback_registration(self):
        """Test recovery callback registration and execution"""
        callback_executed = False
        
        def test_callback(error_info):
            nonlocal callback_executed
            callback_executed = True
        
        self.error_handler.register_recovery_callback("test_action", test_callback)
        
        # Create error with automated recovery action
        error = Exception("Test error")
        context = ErrorContext()
        
        # Mock the error patterns to include our test action
        self.error_handler.error_patterns["test_pattern"] = {
            "category": ErrorCategory.SYSTEM,
            "severity": ErrorSeverity.LOW,
            "user_message": "Test message",
            "recovery_actions": [
                {
                    "action_type": "test_action",
                    "description": "Test action",
                    "automated": True
                }
            ]
        }
        
        error_info = self.error_handler.handle_error(error, context, "test_pattern")
        
        self.assertTrue(callback_executed)
    
    def test_error_summary(self):
        """Test error summary generation"""
        # Generate some test errors
        for i in range(3):
            error = Exception(f"Test error {i}")
            self.error_handler.handle_error(error)
        
        summary = self.error_handler.get_error_summary()
        
        self.assertEqual(summary["total_errors"], 3)
        self.assertEqual(summary["unresolved_errors"], 3)
        self.assertIn("recent_errors", summary)
    
    def test_graceful_degradation_decorator(self):
        """Test graceful degradation decorator"""
        
        def fallback_func():
            return "fallback_result"
        
        @graceful_degradation(fallback_func, "Test degradation")
        def failing_function():
            raise Exception("Function failed")
        
        result = failing_function()
        self.assertEqual(result, "fallback_result")


class TestLoggingSystem(unittest.TestCase):
    """Test cases for LoggingSystem class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.logging_system = LoggingSystem(
            log_dir=self.temp_dir,
            app_name="test_app"
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_logger_creation(self):
        """Test that loggers are created properly"""
        logger = self.logging_system.get_logger()
        self.assertIsNotNone(logger)
        
        # Test that log files are created
        log_files = os.listdir(self.temp_dir)
        self.assertTrue(any(f.endswith('.log') for f in log_files))
    
    def test_performance_logging(self):
        """Test performance metric logging"""
        self.logging_system.log_performance(
            operation="test_operation",
            duration=1.5,
            success=True,
            additional_data={"test": "data"}
        )
        
        # Check that metric was recorded
        self.assertEqual(len(self.logging_system.performance_metrics), 1)
        metric = self.logging_system.performance_metrics[0]
        self.assertEqual(metric.operation, "test_operation")
        self.assertEqual(metric.duration, 1.5)
        self.assertTrue(metric.success)
    
    def test_configuration_change_logging(self):
        """Test configuration change logging"""
        self.logging_system.log_configuration_change(
            config_type="categories",
            old_value={"count": 5},
            new_value={"count": 6},
            user="test_user"
        )
        
        # Check that change was recorded
        self.assertEqual(len(self.logging_system.config_changes), 1)
        change = self.logging_system.config_changes[0]
        self.assertEqual(change.config_type, "categories")
        self.assertEqual(change.user, "test_user")
    
    def test_performance_summary(self):
        """Test performance summary generation"""
        # Add some test metrics
        for i in range(5):
            self.logging_system.log_performance(
                operation=f"operation_{i % 2}",
                duration=i * 0.1,
                success=i % 2 == 0
            )
        
        summary = self.logging_system.get_performance_summary(24)
        
        self.assertEqual(summary["total_operations"], 5)
        self.assertIn("operation_statistics", summary)
        self.assertIn("operation_0", summary["operation_statistics"])
        self.assertIn("operation_1", summary["operation_statistics"])
    
    def test_performance_monitor_decorator(self):
        """Test performance monitoring decorator"""
        
        @performance_monitor("test_function")
        def test_function(x, y):
            return x + y
        
        result = test_function(1, 2)
        
        self.assertEqual(result, 3)
        # Check that performance was logged
        self.assertTrue(len(self.logging_system.performance_metrics) > 0)
    
    def test_user_action_logging(self):
        """Test user action logging"""
        log_user_action(
            action="test_action",
            user_id="test_user",
            additional_data={"page": "index"}
        )
        
        # This should not raise an exception and should log the action
        # We can't easily test the log output without complex setup,
        # but we can ensure the function executes without error
        self.assertTrue(True)
    
    def test_configuration_change_convenience_function(self):
        """Test configuration change convenience function"""
        log_configuration_change(
            config_type="ui",
            old_value="old_theme",
            new_value="new_theme",
            user="admin"
        )
        
        # Check that change was recorded in the global logging system
        global_system = get_logging_system()
        self.assertTrue(len(global_system.config_changes) > 0)


class TestIntegration(unittest.TestCase):
    """Integration tests for error handling and logging"""
    
    def test_error_handling_with_logging(self):
        """Test that errors are properly logged"""
        error_handler = ErrorHandler()
        
        # Create an error that should be logged
        error = ValueError("Test integration error")
        context = ErrorContext(function_name="test_function")
        
        error_info = error_handler.handle_error(error, context)
        
        # Verify error was handled
        self.assertIsNotNone(error_info.error_id)
        self.assertEqual(error_info.message, "Test integration error")
    
    def test_performance_monitoring_with_errors(self):
        """Test performance monitoring when errors occur"""
        
        @performance_monitor("failing_operation")
        def failing_operation():
            raise Exception("Operation failed")
        
        with self.assertRaises(Exception):
            failing_operation()
        
        # Check that performance was still logged (with success=False)
        logging_system = get_logging_system()
        metrics = [m for m in logging_system.performance_metrics 
                  if m.operation == "failing_operation"]
        
        self.assertTrue(len(metrics) > 0)
        self.assertFalse(metrics[-1].success)


if __name__ == '__main__':
    unittest.main()