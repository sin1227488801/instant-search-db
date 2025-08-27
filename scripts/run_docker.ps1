# Docker起動スクリプト（確実版）

Write-Host "========================================" -ForegroundColor Green
Write-Host "instant-search-db Docker起動" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host "`n🐳 Dockerコンテナを起動しています..." -ForegroundColor Yellow

try {
    # 既存のコンテナを停止・削除
    docker-compose down 2>$null
    
    # 新しくビルド・起動
    docker-compose up --build
    
} catch {
    Write-Host "❌ Docker起動に失敗しました" -ForegroundColor Red
    Write-Host "Dockerがインストールされているか確認してください" -ForegroundColor Yellow
    
    Write-Host "`nDocker Desktop のインストール:" -ForegroundColor Cyan
    Write-Host "https://www.docker.com/products/docker-desktop/" -ForegroundColor White
    
    Read-Host "`n何かキーを押してください"
}