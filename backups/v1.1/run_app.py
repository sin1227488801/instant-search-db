#!/usr/bin/env python3
"""アプリケーション起動スクリプト"""

if __name__ == '__main__':
    from instant_search_db import create_app
    
    app = create_app()
    print("🚀 ローグライクゲーム アイテム検索データベースを起動しています...")
    print("📱 ブラウザで http://127.0.0.1:5000 にアクセスしてください")
    print("⏹️  停止するには Ctrl+C を押してください")
    app.run(host='0.0.0.0', port=5000, debug=True)