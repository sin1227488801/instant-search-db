#!/usr/bin/env python3
"""アプリケーション起動スクリプト"""

import sys
import os
from instant_search_db.config_manager import ConfigManager
from instant_search_db.logging_system import get_logging_system, LogCategory

def initialize_configuration():
    """Initialize and validate configuration system"""
    try:
        # Initialize configuration manager
        config_manager = ConfigManager()
        
        # Get logger for startup messages
        logger = get_logging_system().get_logger(LogCategory.SYSTEM)
        
        # Perform configuration validation
        logger.info("Validating configuration system...")
        is_valid = config_manager.validate_all_configs()
        
        if not is_valid:
            logger.warning("Configuration validation found issues, but continuing with fallback configurations")
        
        # Perform health check
        health_status = config_manager.health_check()
        logger.info(f"Configuration system health: {health_status['overall_status']}")
        
        if health_status['overall_status'] == 'unhealthy':
            logger.error("Configuration system is unhealthy. Check configuration files.")
            for issue in health_status.get('issues', []):
                logger.error(f"  - {issue}")
        
        return config_manager, is_valid
        
    except Exception as e:
        print(f"❌ Configuration initialization failed: {e}")
        print("   Continuing with default configuration...")
        return None, False

if __name__ == '__main__':
    # Initialize configuration system
    config_manager, config_valid = initialize_configuration()
    
    # Create Flask application
    from instant_search_db import create_app
    
    try:
        app = create_app()
        
        # Display startup messages
        if config_manager:
            ui_config = config_manager.load_ui_settings()
            app_title = ui_config.title
        else:
            app_title = "汎用データベース検索システム"
        
        print(f"🚀 {app_title}を起動しています...")
        print("📱 ブラウザで http://127.0.0.1:5000 にアクセスしてください")
        print("⏹️  停止するには Ctrl+C を押してください")
        
        if not config_valid:
            print("⚠️  設定ファイルに問題があります。デフォルト設定で動作しています。")
        
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except Exception as e:
        print(f"❌ アプリケーションの起動に失敗しました: {e}")
        sys.exit(1)