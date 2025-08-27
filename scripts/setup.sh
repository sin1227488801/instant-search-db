#!/bin/bash
# ローグライクゲーム アイテム検索データベース - セットアップスクリプト

echo "🚀 ローグライクゲーム アイテム検索データベース セットアップ"
echo "============================================================"

# Docker が利用可能かチェック
echo "📋 環境チェック中..."

if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "✅ Docker が見つかりました"
    echo "✅ Docker Compose が見つかりました"
    echo ""
    echo "🐳 Docker で起動します（推奨）"
    echo "docker-compose up --build を実行中..."
    
    docker-compose up --build
    exit 0
fi

echo "⚠️  Docker が見つかりません。Python で起動します"

# Python チェック
PYTHON_CMD=""
for cmd in python3 python py; do
    if command -v $cmd &> /dev/null; then
        PYTHON_CMD=$cmd
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "❌ Python が見つかりません"
    echo "Python をインストールしてください"
    exit 1
fi

echo "✅ Python が見つかりました: $PYTHON_CMD"

# 依存関係インストール
echo ""
echo "📦 依存関係をインストール中..."
$PYTHON_CMD -m pip install flask

if [ $? -ne 0 ]; then
    echo "❌ 依存関係のインストールに失敗しました"
    exit 1
fi

# アプリケーション起動
echo ""
echo "🚀 アプリケーションを起動中..."
$PYTHON_CMD run_app.py