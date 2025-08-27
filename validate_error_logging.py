#!/usr/bin/env python3
"""
Validation script for error handling and logging system.
This script tests the basic functionality without requiring external test frameworks.
"""

import os
import sys
import tempfile
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_error_handler():
    """Test basic error handler functionality"""
    print("Testing Error Handler...")
    
    try:
        from instant_search_db.error_handler import ErrorHandler, ErrorContext, ErrorSeverity, ErrorCategory
        
        # Create error handler
        error_handler = ErrorHandler()
        
        # Test basic error handling
        error = FileNotFoundError("Test config file not found")
        context = ErrorContext(file_path="/test/config.json", function_name="test_function")
        
        error_info = error_handler.handle_error(error, context, "config_file_not_found")
        
        # Validate error info
        assert error_info.category == ErrorCategory.CONFIGURATION
        assert error_info.severity == ErrorSeverity.MEDIUM
        assert "設定ファイルが見つかりません" in error_info.user_message
        assert len(error_info.recovery_actions) > 0
        
        print("✓ Error handler basic functionality works")
        
        # Test error summary
        summary = error_handler.get_error_summary()
        assert summary["total_errors"] >= 1
        assert "recent_errors" in summary
        
        print("✓ Error summary generation works")
        
        return True
        
    except Exception as e:
        print(f"✗ Error handler test failed: {e}")
        return False

def test_logging_system():
    """Test basic logging system functionality"""
    print("Testing Logging System...")
    
    try:
        from instant_search_db.logging_system import LoggingSystem, LogCategory, performance_monitor
        
        # Create temporary directory for logs
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create logging system
            logging_system = LoggingSystem(
                log_dir=temp_dir,
                app_name="validation_test"
            )
            
            # Test logger creation
            logger = logging_system.get_logger(LogCategory.SYSTEM)
            assert logger is not None
            
            print("✓ Logger creation works")
            
            # Test performance logging
            logging_system.log_performance(
                operation="test_operation",
                duration=1.5,
                success=True,
                additional_data={"test": "data"}
            )
            
            assert len(logging_system.performance_metrics) == 1
            metric = logging_system.performance_metrics[0]
            assert metric.operation == "test_operation"
            assert metric.duration == 1.5
            assert metric.success == True
            
            print("✓ Performance logging works")
            
            # Test configuration change logging
            logging_system.log_configuration_change(
                config_type="categories",
                old_value={"count": 5},
                new_value={"count": 6},
                user="test_user"
            )
            
            assert len(logging_system.config_changes) == 1
            change = logging_system.config_changes[0]
            assert change.config_type == "categories"
            assert change.user == "test_user"
            
            print("✓ Configuration change logging works")
            
            # Test performance summary
            summary = logging_system.get_performance_summary(24)
            assert summary["total_operations"] == 1
            assert summary["successful_operations"] == 1
            assert "operation_statistics" in summary
            
            print("✓ Performance summary generation works")
            
            # Test performance monitor decorator
            @performance_monitor("test_decorated_function")
            def test_function(x, y):
                return x + y
            
            result = test_function(1, 2)
            assert result == 3
            
            # Should have 2 metrics now (1 manual + 1 from decorator)
            assert len(logging_system.performance_metrics) == 2
            
            print("✓ Performance monitor decorator works")
            
            return True
            
        finally:
            # Clean up temporary directory
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except Exception as e:
        print(f"✗ Logging system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration():
    """Test integration between error handling and logging"""
    print("Testing Integration...")
    
    try:
        from instant_search_db.error_handler import ErrorHandler
        from instant_search_db.logging_system import LoggingSystem
        
        # Create temporary directory for logs
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create logging system
            logging_system = LoggingSystem(log_dir=temp_dir, app_name="integration_test")
            logger = logging_system.get_logger()
            
            # Create error handler with the logger
            error_handler = ErrorHandler(logger)
            
            # Test that errors are handled and logged
            error = ValueError("Integration test error")
            error_info = error_handler.handle_error(error)
            
            assert error_info.error_id is not None
            assert error_info.message == "Integration test error"
            
            print("✓ Error handling and logging integration works")
            
            return True
            
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_graceful_degradation():
    """Test graceful degradation functionality"""
    print("Testing Graceful Degradation...")
    
    try:
        from instant_search_db.error_handler import graceful_degradation
        
        def fallback_function():
            return "fallback_result"
        
        @graceful_degradation(fallback_function, "Test graceful degradation")
        def failing_function():
            raise Exception("Function intentionally failed")
        
        result = failing_function()
        assert result == "fallback_result"
        
        print("✓ Graceful degradation works")
        
        return True
        
    except Exception as e:
        print(f"✗ Graceful degradation test failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("=" * 50)
    print("Error Handling and Logging System Validation")
    print("=" * 50)
    
    tests = [
        test_error_handler,
        test_logging_system,
        test_integration,
        test_graceful_degradation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print()
        if test():
            passed += 1
        else:
            print("Test failed!")
    
    print()
    print("=" * 50)
    print(f"Validation Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! Error handling and logging system is working correctly.")
        return 0
    else:
        print("✗ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())