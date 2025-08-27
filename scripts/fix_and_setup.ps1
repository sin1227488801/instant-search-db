# instant-search-db 完全クリーンアップ & セットアップスクリプト

Write-Host "========================================" -ForegroundColor Red
Write-Host "instant-search-db 完全リセット & セットアップ" -ForegroundColor Red  
Write-Host "========================================" -ForegroundColor Red

# 1. 古い仮想環境の完全削除
Write-Host "`n🗑️ 古い仮想環境をクリーンアップ中..." -ForegroundColor Yellow

if (Test-Path "venv") {
    Write-Host "古い仮想環境を削除しています..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "venv" -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "✅ 古い仮想環境を削除しました" -ForegroundColor Green
}

# 2. Pythonの確認と修復
Write-Host "`n🐍 Python環境を確認中..." -ForegroundColor Yellow

# 利用可能なPythonコマンドを探す
$pythonCommands = @("python", "python3", "py")
$workingPython = $null

foreach ($cmd in $pythonCommands) {
    try {
        $version = & $cmd --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $workingPython = $cmd
            Write-Host "✅ 動作するPython発見: $cmd" -ForegroundColor Green
            Write-Host "   バージョン: $version" -ForegroundColor Cyan
            break
        }
    } catch {
        # 無視
    }
}

if (-not $workingPython) {
    Write-Host "❌ 動作するPythonが見つかりません" -ForegroundColor Red
    Write-Host "`n📥 Pythonをインストールします..." -ForegroundColor Yellow
    
    # Microsoft Store版Pythonのインストールを試行
    Write-Host "Microsoft Store版Pythonのインストールを試行中..." -ForegroundColor Yellow
    try {
        Start-Process "ms-windows-store://pdp/?ProductId=9NRWMJP3717K" -Wait
        Write-Host "Microsoft Storeが開きました。Pythonをインストールしてから再実行してください。" -ForegroundColor Cyan
    } catch {
        Write-Host "Microsoft Storeを開けませんでした。" -ForegroundColor Yellow
    }
    
    Write-Host "`n手動インストール方法:" -ForegroundColor Cyan
    Write-Host "1. https://www.python.org/downloads/ にアクセス" -ForegroundColor White
    Write-Host "2. 最新版をダウンロード" -ForegroundColor White
    Write-Host "3. インストール時に 'Add Python to PATH' にチェック" -ForegroundColor White
    Write-Host "4. インストール後、PowerShellを再起動" -ForegroundColor White
    Write-Host "5. このスクリプトを再実行" -ForegroundColor White
    
    Read-Host "`nPythonインストール後、何かキーを押してください"
    exit 1
}

# 3. 新しい仮想環境の作成
Write-Host "`n📦 新しい仮想環境を作成中..." -ForegroundColor Yellow
& $workingPython -m venv venv --clear
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 仮想環境の作成に失敗しました" -ForegroundColor Red
    Write-Host "venvモジュールをインストールします..." -ForegroundColor Yellow
    & $workingPython -m pip install virtualenv
    & $workingPython -m virtualenv venv
}

Write-Host "✅ 新しい仮想環境を作成しました" -ForegroundColor Green

# 4. 仮想環境の有効化
Write-Host "`n🔄 仮想環境を有効化中..." -ForegroundColor Yellow

# PowerShellの実行ポリシーを設定
try {
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    Write-Host "✅ PowerShell実行ポリシーを設定しました" -ForegroundColor Green
} catch {
    Write-Host "⚠️ 実行ポリシーの設定に失敗しましたが続行します" -ForegroundColor Yellow
}

# 仮想環境を有効化
try {
    & ".\venv\Scripts\Activate.ps1"
    Write-Host "✅ 仮想環境を有効化しました" -ForegroundColor Green
} catch {
    Write-Host "❌ 仮想環境の有効化に失敗しました" -ForegroundColor Red
    Write-Host "手動で有効化してください: venv\Scripts\activate" -ForegroundColor Yellow
}

# 5. pipのアップグレード
Write-Host "`n⬆️ pipをアップグレード中..." -ForegroundColor Yellow
python -m pip install --upgrade pip
Write-Host "✅ pipをアップグレードしました" -ForegroundColor Green

# 6. 依存関係のインストール
Write-Host "`n📚 依存関係をインストール中..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 依存関係のインストールに失敗しました" -ForegroundColor Red
    Write-Host "個別にインストールを試行します..." -ForegroundColor Yellow
    
    pip install Flask==3.0.0
    pip install Werkzeug==3.0.1
    pip install pytest==7.4.3
}

Write-Host "✅ 依存関係をインストールしました" -ForegroundColor Green

# 7. 環境テスト
Write-Host "`n🧪 環境テストを実行中..." -ForegroundColor Yellow
python quick_test.py

# 8. アプリケーション起動の確認
Write-Host "`n🚀 アプリケーション起動準備完了！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "次のコマンドでアプリケーションを起動できます:" -ForegroundColor Cyan
Write-Host "python -m instant_search_db" -ForegroundColor White
Write-Host "`nまたは自動起動しますか？ (y/N)" -ForegroundColor Yellow

$response = Read-Host
if ($response -eq "y" -or $response -eq "Y") {
    Write-Host "`nアプリケーションを起動します..." -ForegroundColor Green
    Write-Host "ブラウザで http://127.0.0.1:5000 にアクセスしてください" -ForegroundColor Cyan
    Write-Host "停止するには Ctrl+C を押してください" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Green
    
    python -m instant_search_db
} else {
    Write-Host "`n✅ セットアップが完了しました！" -ForegroundColor Green
    Write-Host "アプリケーションを起動するには:" -ForegroundColor Cyan
    Write-Host "python -m instant_search_db" -ForegroundColor White
}