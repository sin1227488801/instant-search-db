"""
Instant Search Database Package
Enhanced with comprehensive error handling, logging system, and configuration management
"""

import os
import logging
from flask import Flask
from .routes import bp
from .models import init_db
from .logging_system import initialize_logging, get_logging_system, LogCategory
from .error_handler import get_error_handler
from .config_manager import ConfigManager

def setup_application_logging():
    """Setup application-wide logging and error handling"""
    try:
        # Initialize logging system
        log_dir = os.environ.get('LOG_DIR', 'logs')
        app_name = os.environ.get('APP_NAME', 'instant_search_db')
        
        logging_system = initialize_logging(
            log_dir=log_dir,
            app_name=app_name
        )
        
        # Get main logger
        logger = logging_system.get_logger(LogCategory.SYSTEM)
        logger.info("Application logging system initialized")
        
        # Initialize error handler
        error_handler = get_error_handler()
        logger.info("Error handling system initialized")
        
        return True, logger
        
    except Exception as e:
        # Fallback to basic logging if initialization fails
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to initialize enhanced logging system: {e}")
        return False, logger

def initialize_configuration_system():
    """Initialize and validate configuration system"""
    try:
        # Get project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        config_dir = os.path.join(project_root, 'config')
        
        # Initialize configuration manager
        config_manager = ConfigManager(config_dir)
        
        # Get logger for configuration messages
        logger = get_logging_system().get_logger(LogCategory.CONFIGURATION)
        
        # Validate all configurations
        logger.info("Initializing configuration system...")
        is_valid = config_manager.validate_all_configs()
        
        if is_valid:
            logger.info("Configuration system initialized successfully")
        else:
            logger.warning("Configuration validation found issues, using fallback configurations")
        
        # Perform health check
        health_status = config_manager.health_check()
        logger.info(f"Configuration health status: {health_status['overall_status']}")
        
        # Log any configuration issues
        if 'issues' in health_status:
            for issue in health_status['issues']:
                logger.warning(f"Configuration issue: {issue}")
        
        return config_manager, is_valid
        
    except Exception as e:
        # Fallback to basic logging if configuration system fails
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to initialize configuration system: {e}")
        logger.info("Continuing with default configuration")
        return None, False

def create_app():
    """Create Flask application with enhanced logging, error handling, and configuration management"""
    
    # Initialize logging system first
    logging_success, logger = setup_application_logging()
    
    if logging_success:
        logger.info("Starting application initialization")
    
    # Initialize configuration system
    config_manager, config_valid = initialize_configuration_system()
    
    # 現在のファイルの場所から相対的にパスを設定
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    template_dir = os.path.join(project_root, 'templates')
    static_dir = os.path.join(project_root, 'static')
    
    logger.info(f"Template directory: {template_dir}")
    logger.info(f"Static directory: {static_dir}")
    logger.info(f"Template exists: {os.path.exists(template_dir)}")
    logger.info(f"Index.html exists: {os.path.exists(os.path.join(template_dir, 'index.html'))}")
    
    try:
        app = Flask(__name__, 
                    template_folder=template_dir,
                    static_folder=static_dir)
        
        # Store configuration manager in app context for access by routes
        app.config_manager = config_manager
        app.config_valid = config_valid
        
        # Configure Flask logging to use our logging system
        if logging_success:
            app.logger.handlers = []  # Remove default handlers
            app.logger.addHandler(logger.handlers[0] if logger.handlers else logging.StreamHandler())
            app.logger.setLevel(logging.INFO)
        
        app.register_blueprint(bp)
        
        # データベース初期化 with error handling
        try:
            init_db()
            logger.info("Database initialization completed")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            if logging_success:
                error_handler = get_error_handler()
                error_handler.handle_error(e, None)
        
        # Log configuration status
        if config_manager:
            logger.info("Application created with configuration system enabled")
        else:
            logger.warning("Application created with default configuration (configuration system failed)")
        
        logger.info("Flask application created successfully")
        return app
        
    except Exception as e:
        logger.error(f"Failed to create Flask application: {e}")
        if logging_success:
            error_handler = get_error_handler()
            error_handler.handle_error(e, None)
        raise

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)