#!/usr/bin/env python3
"""
instant_search_db パッケージのメインエントリーポイント
python -m instant_search_db で実行される
"""

import sys
from . import create_app
from .config_manager import ConfigManager
from .logging_system import get_logging_system, LogCategory

def main():
    """メイン関数"""
    try:
        # Create Flask application (includes configuration initialization)
        app = create_app()
        
        # Get application title from configuration if available
        app_title = "汎用データベース検索システム"
        config_status = "✅ 設定システム: 正常"
        
        if hasattr(app, 'config_manager') and app.config_manager:
            try:
                ui_config = app.config_manager.load_ui_settings()
                app_title = ui_config.title
                
                if not app.config_valid:
                    config_status = "⚠️  設定システム: 警告あり (デフォルト設定使用)"
            except Exception as e:
                config_status = f"❌ 設定システム: エラー ({e})"
        else:
            config_status = "⚠️  設定システム: 無効 (デフォルト設定使用)"
        
        # Display startup information
        print(f"🚀 {app_title}を起動しています...")
        print(f"   {config_status}")
        print("📱 ブラウザで http://127.0.0.1:5000 にアクセスしてください")
        print("⏹️  停止するには Ctrl+C を押してください")
        
        # Start the application
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except Exception as e:
        print(f"❌ アプリケーションの起動に失敗しました: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()