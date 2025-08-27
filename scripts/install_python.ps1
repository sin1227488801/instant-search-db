# Python自動インストールスクリプト

Write-Host "========================================" -ForegroundColor Green
Write-Host "Python自動インストール" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# 管理者権限チェック
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

Write-Host "`n🔍 インストール方法を選択してください:" -ForegroundColor Yellow
Write-Host "1. Microsoft Store版Python（推奨・簡単）" -ForegroundColor White
Write-Host "2. winget使用（Windows 10/11）" -ForegroundColor White
Write-Host "3. 公式サイトを開く" -ForegroundColor White
Write-Host "4. 診断のみ実行" -ForegroundColor White

$choice = Read-Host "`n選択 (1-4)"

switch ($choice) {
    "1" {
        Write-Host "`n📱 Microsoft Storeを開いています..." -ForegroundColor Yellow
        try {
            Start-Process "ms-windows-store://search/?query=python"
            Write-Host "✅ Microsoft Storeが開きました" -ForegroundColor Green
            Write-Host "Pythonを検索してインストールしてください" -ForegroundColor Cyan
            Write-Host "インストール後、PowerShellを再起動してください" -ForegroundColor Cyan
        } catch {
            Write-Host "❌ Microsoft Storeを開けませんでした" -ForegroundColor Red
        }
    }
    
    "2" {
        Write-Host "`n📦 wingetでPythonをインストール中..." -ForegroundColor Yellow
        try {
            winget install Python.Python.3.11
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Pythonのインストールが完了しました" -ForegroundColor Green
                Write-Host "PowerShellを再起動してください" -ForegroundColor Cyan
            } else {
                Write-Host "❌ wingetインストールに失敗しました" -ForegroundColor Red
            }
        } catch {
            Write-Host "❌ wingetが利用できません" -ForegroundColor Red
            Write-Host "Microsoft Store版または公式サイト版を使用してください" -ForegroundColor Yellow
        }
    }
    
    "3" {
        Write-Host "`n🌐 公式サイトを開いています..." -ForegroundColor Yellow
        try {
            Start-Process "https://www.python.org/downloads/"
            Write-Host "✅ 公式サイトが開きました" -ForegroundColor Green
            Write-Host "最新版をダウンロードしてインストールしてください" -ForegroundColor Cyan
            Write-Host "⚠️ インストール時に 'Add Python to PATH' にチェックを入れてください" -ForegroundColor Yellow
        } catch {
            Write-Host "❌ ブラウザを開けませんでした" -ForegroundColor Red
        }
    }
    
    "4" {
        Write-Host "`n🔍 診断スクリプトを実行します..." -ForegroundColor Yellow
        & .\diagnose_python.ps1
        return
    }
    
    default {
        Write-Host "❌ 無効な選択です" -ForegroundColor Red
        return
    }
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "インストール後の確認手順" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host "1. PowerShellを再起動" -ForegroundColor Yellow
Write-Host "2. 以下のコマンドでPythonを確認:" -ForegroundColor Yellow
Write-Host "   python --version" -ForegroundColor White
Write-Host "3. 仮想環境を作成:" -ForegroundColor Yellow
Write-Host "   python -m venv venv" -ForegroundColor White
Write-Host "4. 仮想環境を有効化:" -ForegroundColor Yellow
Write-Host "   venv\Scripts\activate" -ForegroundColor White
Write-Host "5. 依存関係をインストール:" -ForegroundColor Yellow
Write-Host "   pip install -r requirements.txt" -ForegroundColor White

Read-Host "`n何かキーを押してください"