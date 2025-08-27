#!/usr/bin/env pwsh
# ローグライクゲーム アイテム検索データベース - セットアップスクリプト

Write-Host "🚀 ローグライクゲーム アイテム検索データベース セットアップ" -ForegroundColor Cyan
Write-Host "=" * 60

# Docker が利用可能かチェック
Write-Host "📋 環境チェック中..." -ForegroundColor Yellow

if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "✅ Docker が見つかりました" -ForegroundColor Green
    
    if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
        Write-Host "✅ Docker Compose が見つかりました" -ForegroundColor Green
        Write-Host ""
        Write-Host "🐳 Docker で起動します（推奨）" -ForegroundColor Cyan
        Write-Host "docker-compose up --build を実行中..."
        
        docker-compose up --build
        exit 0
    }
}

Write-Host "⚠️  Docker が見つかりません。Python で起動します" -ForegroundColor Yellow

# Python チェック
$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        $pythonCmd = $cmd
        break
    }
}

if (-not $pythonCmd) {
    Write-Host "❌ Python が見つかりません" -ForegroundColor Red
    Write-Host "Python をインストールしてください: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Python が見つかりました: $pythonCmd" -ForegroundColor Green

# 依存関係インストール
Write-Host ""
Write-Host "📦 依存関係をインストール中..." -ForegroundColor Yellow
& $pythonCmd -m pip install flask

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 依存関係のインストールに失敗しました" -ForegroundColor Red
    exit 1
}

# アプリケーション起動
Write-Host ""
Write-Host "🚀 アプリケーションを起動中..." -ForegroundColor Cyan
& $pythonCmd run_app.py