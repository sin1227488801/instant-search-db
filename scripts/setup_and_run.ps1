# instant-search-db セットアップ & 起動スクリプト (PowerShell)

Write-Host "========================================" -ForegroundColor Green
Write-Host "instant-search-db セットアップ & 起動" -ForegroundColor Green  
Write-Host "========================================" -ForegroundColor Green

# 現在のディレクトリを確認
Write-Host "現在のディレクトリ: $PWD" -ForegroundColor Yellow

# Pythonの確認
Write-Host "`nPython環境を確認中..." -ForegroundColor Yellow

$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
}

if (-not $pythonCmd) {
    Write-Host "Pythonが見つかりません。以下からインストールしてください:" -ForegroundColor Red
    Write-Host "https://www.python.org/downloads/" -ForegroundColor Red
    Read-Host "続行するには何かキーを押してください"
    exit 1
}

& $pythonCmd --version
Write-Host "Python実行コマンド: $pythonCmd" -ForegroundColor Green

# 仮想環境の作成
Write-Host "`n仮想環境を作成中..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    & $pythonCmd -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "仮想環境の作成に失敗しました。" -ForegroundColor Red
        Read-Host "続行するには何かキーを押してください"
        exit 1
    }
    Write-Host "仮想環境を作成しました。" -ForegroundColor Green
} else {
    Write-Host "仮想環境は既に存在します。" -ForegroundColor Green
}

# 仮想環境の有効化
Write-Host "`n仮想環境を有効化中..." -ForegroundColor Yellow
try {
    & "venv\Scripts\Activate.ps1"
    Write-Host "仮想環境を有効化しました。" -ForegroundColor Green
} catch {
    Write-Host "PowerShellの実行ポリシーを変更します..." -ForegroundColor Yellow
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    & "venv\Scripts\Activate.ps1"
}

# pipのアップグレード
Write-Host "`npipをアップグレード中..." -ForegroundColor Yellow
& python -m pip install --upgrade pip

# 依存関係のインストール
Write-Host "`n依存関係をインストール中..." -ForegroundColor Yellow
& pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "依存関係のインストールに失敗しました。" -ForegroundColor Red
    Read-Host "続行するには何かキーを押してください"
    exit 1
}

# アプリケーションの起動
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "アプリケーションを起動します..." -ForegroundColor Green
Write-Host "ブラウザで http://127.0.0.1:5000 にアクセスしてください" -ForegroundColor Cyan
Write-Host "停止するには Ctrl+C を押してください" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Green

& python -m instant_search_db