#!/bin/bash

echo "========================================"
echo "instant-search-db セットアップ & 起動"
echo "========================================"

# 現在のディレクトリを確認
echo "現在のディレクトリ: $(pwd)"

# Pythonの確認
echo ""
echo "Python環境を確認中..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "Pythonが見つかりません。以下からインストールしてください:"
        echo "Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
        echo "Mac: brew install python3"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

$PYTHON_CMD --version
echo ""

# 仮想環境の作成
echo "仮想環境を作成中..."
if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        echo "仮想環境の作成に失敗しました。"
        exit 1
    fi
    echo "仮想環境を作成しました。"
else
    echo "仮想環境は既に存在します。"
fi

# 仮想環境の有効化
echo ""
echo "仮想環境を有効化中..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "仮想環境の有効化に失敗しました。"
    exit 1
fi

# pipのアップグレード
echo ""
echo "pipをアップグレード中..."
python -m pip install --upgrade pip

# 依存関係のインストール
echo ""
echo "依存関係をインストール中..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "依存関係のインストールに失敗しました。"
    exit 1
fi

# アプリケーションの起動
echo ""
echo "========================================"
echo "アプリケーションを起動します..."
echo "ブラウザで http://127.0.0.1:5000 にアクセスしてください"
echo "停止するには Ctrl+C を押してください"
echo "========================================"
echo ""

python -m instant_search_db