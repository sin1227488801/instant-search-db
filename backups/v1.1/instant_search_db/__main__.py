#!/usr/bin/env python3
"""
instant_search_db パッケージのメインエントリーポイント
python -m instant_search_db で実行される
"""

from . import create_app

def main():
    """メイン関数"""
    app = create_app()
    print("🚀 instant-search-db を起動しています...")
    print("📱 ブラウザで http://127.0.0.1:5000 にアクセスしてください")
    print("⏹️  停止するには Ctrl+C を押してください")
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()