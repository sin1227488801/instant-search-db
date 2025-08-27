#!/usr/bin/env python3
"""
Test script for enhanced error handling and logging system
"""

def test_error_handling_and_logging():
    """Test the enhanced error handling and logging system"""
    print("Testing Enhanced Error Handling and Logging System...")
    print("=" * 60)
    
    try:
        # Test 1: Import modules
        print("1. Testing module imports...")
        from instant_search_db.error_handler import ErrorHandler, ErrorContext
        from instant_search_db.logging_system import LoggingSystem, LogCategory
        print("   ✓ Modules imported successfully")
        
        # Test 2: Create error handler
        print("2. Testing error handler creation...")
        error_handler = ErrorHandler()
        print("   ✓ Error handler created successfully")
        
        # Test 3: Create logging system
        print("3. Testing logging system creation...")
        logging_system = LoggingSystem(log_dir="test_logs", app_name="test_app")
        print("   ✓ Logging system created successfully")
        
        # Test 4: Test error handling
        print("4. Testing error handling...")
        test_error = FileNotFoundError("Test configuration file not found")
        context = ErrorContext(file_path="test_config.json", function_name="test_function")
        error_info = error_handler.handle_error(test_error, context, "config_file_not_found")
        print(f"   ✓ Error handled with ID: {error_info.error_id}")
        print(f"   ✓ User message: {error_info.user_message}")
        
        # Test 5: Test performance logging
        print("5. Testing performance logging...")
        logging_system.log_performance("test_operation", 1.5, success=True)
        print(f"   ✓ Performance logged. Total metrics: {len(logging_system.performance_metrics)}")
        
        # Test 6: Test configuration change logging
        print("6. Testing configuration change logging...")
        logging_system.log_configuration_change("test_config", "old_value", "new_value", "test_user")
        print(f"   ✓ Config change logged. Total changes: {len(logging_system.config_changes)}")
        
        # Test 7: Test performance summary
        print("7. Testing performance summary...")
        summary = logging_system.get_performance_summary(24)
        print(f"   ✓ Performance summary generated. Total operations: {summary['total_operations']}")
        
        # Test 8: Test error summary
        print("8. Testing error summary...")
        error_summary = error_handler.get_error_summary()
        print(f"   ✓ Error summary generated. Total errors: {error_summary['total_errors']}")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED! Enhanced system is working correctly.")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_application_integration():
    """Test integration with the main application"""
    print("\nTesting Application Integration...")
    print("=" * 60)
    
    try:
        # Test application creation with enhanced logging
        print("1. Testing application creation...")
        from instant_search_db import create_app
        app = create_app()
        print("   ✓ Application created successfully with enhanced logging")
        
        # Test that logging system is initialized
        print("2. Testing logging system initialization...")
        from instant_search_db.logging_system import get_logging_system
        logging_system = get_logging_system()
        print(f"   ✓ Global logging system available with {len(logging_system.loggers)} loggers")
        
        # Test that error handler is available
        print("3. Testing error handler availability...")
        from instant_search_db.error_handler import get_error_handler
        error_handler = get_error_handler()
        print("   ✓ Global error handler available")
        
        print("\n" + "=" * 60)
        print("✅ APPLICATION INTEGRATION TESTS PASSED!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ INTEGRATION TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("Enhanced Error Handling and Logging System Test")
    print("=" * 60)
    
    # Run basic tests
    basic_success = test_error_handling_and_logging()
    
    # Run integration tests
    integration_success = test_application_integration()
    
    if basic_success and integration_success:
        print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("The enhanced error handling and logging system is ready for use.")
    else:
        print("\n⚠️  SOME TESTS FAILED!")
        print("Please check the implementation and fix any issues.")