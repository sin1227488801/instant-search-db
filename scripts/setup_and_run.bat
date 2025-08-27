@echo off
echo ========================================
echo instant-search-db セットアップ & 起動
echo ========================================

REM 現在のディレクトリを確認
echo 現在のディレクトリ: %CD%

REM Pythonの確認
echo.
echo Python環境を確認中...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Pythonが見つかりません。以下からインストールしてください:
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

python --version
echo.

REM 仮想環境の作成
echo 仮想環境を作成中...
if not exist "venv" (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo 仮想環境の作成に失敗しました。
        pause
        exit /b 1
    )
    echo 仮想環境を作成しました。
) else (
    echo 仮想環境は既に存在します。
)

REM 仮想環境の有効化
echo.
echo 仮想環境を有効化中...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo 仮想環境の有効化に失敗しました。
    pause
    exit /b 1
)

REM pipのアップグレード
echo.
echo pipをアップグレード中...
python -m pip install --upgrade pip

REM 依存関係のインストール
echo.
echo 依存関係をインストール中...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 依存関係のインストールに失敗しました。
    pause
    exit /b 1
)

REM アプリケーションの起動
echo.
echo ========================================
echo アプリケーションを起動します...
echo ブラウザで http://127.0.0.1:5000 にアクセスしてください
echo 停止するには Ctrl+C を押してください
echo ========================================
echo.

python -m instant_search_db

pause