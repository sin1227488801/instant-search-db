# Python環境診断スクリプト

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Python環境診断" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. 利用可能なPythonコマンドを確認
Write-Host "`n🔍 利用可能なPythonコマンドを検索中..." -ForegroundColor Yellow

$pythonCommands = @("python", "python3", "py")
$foundPython = @()

foreach ($cmd in $pythonCommands) {
    try {
        $path = Get-Command $cmd -ErrorAction SilentlyContinue
        if ($path) {
            try {
                $version = & $cmd --version 2>$null
                if ($LASTEXITCODE -eq 0) {
                    $foundPython += @{
                        Command = $cmd
                        Path = $path.Source
                        Version = $version
                        Working = $true
                    }
                    Write-Host "✅ $cmd : $version" -ForegroundColor Green
                    Write-Host "   パス: $($path.Source)" -ForegroundColor Gray
                } else {
                    $foundPython += @{
                        Command = $cmd
                        Path = $path.Source
                        Version = "エラー"
                        Working = $false
                    }
                    Write-Host "❌ $cmd : 実行エラー" -ForegroundColor Red
                }
            } catch {
                Write-Host "❌ $cmd : 実行失敗" -ForegroundColor Red
            }
        }
    } catch {
        Write-Host "❌ $cmd : 見つかりません" -ForegroundColor Red
    }
}

# 2. 動作するPythonがあるかチェック
$workingPython = $foundPython | Where-Object { $_.Working -eq $true } | Select-Object -First 1

if ($workingPython) {
    Write-Host "`n✅ 動作するPython発見: $($workingPython.Command)" -ForegroundColor Green
    
    # 3. venvモジュールの確認
    Write-Host "`n🔍 venvモジュールの確認..." -ForegroundColor Yellow
    try {
        & $workingPython.Command -m venv --help >$null 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ venvモジュール利用可能" -ForegroundColor Green
        } else {
            Write-Host "❌ venvモジュール利用不可" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ venvモジュールテスト失敗" -ForegroundColor Red
    }
    
    # 4. pipの確認
    Write-Host "`n🔍 pipの確認..." -ForegroundColor Yellow
    try {
        & $workingPython.Command -m pip --version >$null 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pipVersion = & $workingPython.Command -m pip --version
            Write-Host "✅ pip利用可能: $pipVersion" -ForegroundColor Green
        } else {
            Write-Host "❌ pip利用不可" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ pipテスト失敗" -ForegroundColor Red
    }
    
} else {
    Write-Host "`n❌ 動作するPythonが見つかりません" -ForegroundColor Red
}

# 5. Microsoft Store版Pythonの確認
Write-Host "`n🔍 Microsoft Store版Pythonの確認..." -ForegroundColor Yellow
$msStorePython = Get-AppxPackage -Name "*Python*" -ErrorAction SilentlyContinue
if ($msStorePython) {
    Write-Host "✅ Microsoft Store版Python発見:" -ForegroundColor Green
    $msStorePython | ForEach-Object {
        Write-Host "   $($_.Name) - $($_.Version)" -ForegroundColor Gray
    }
} else {
    Write-Host "❌ Microsoft Store版Python未インストール" -ForegroundColor Red
}

# 6. 推奨アクション
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "推奨アクション" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($workingPython) {
    Write-Host "✅ Pythonは利用可能です" -ForegroundColor Green
    Write-Host "`n次のコマンドで仮想環境を作成してください:" -ForegroundColor Yellow
    Write-Host "$($workingPython.Command) -m venv venv" -ForegroundColor White
    
    Write-Host "`n仮想環境の有効化:" -ForegroundColor Yellow
    Write-Host "venv\Scripts\activate" -ForegroundColor White
    Write-Host "# または" -ForegroundColor Gray
    Write-Host "venv\Scripts\Activate.ps1" -ForegroundColor White
    
} else {
    Write-Host "❌ Pythonのインストールが必要です" -ForegroundColor Red
    Write-Host "`n推奨インストール方法:" -ForegroundColor Yellow
    
    Write-Host "`n1. Microsoft Store版（推奨・簡単）:" -ForegroundColor Cyan
    Write-Host "   Microsoft Storeで 'Python' を検索してインストール" -ForegroundColor White
    
    Write-Host "`n2. 公式サイト版:" -ForegroundColor Cyan
    Write-Host "   https://www.python.org/downloads/" -ForegroundColor White
    Write-Host "   ダウンロード時に 'Add Python to PATH' にチェック" -ForegroundColor White
    
    Write-Host "`n3. winget使用:" -ForegroundColor Cyan
    Write-Host "   winget install Python.Python.3.11" -ForegroundColor White
}

Write-Host "`n🐳 確実な代替案: Docker使用" -ForegroundColor Cyan
Write-Host "docker-compose up --build" -ForegroundColor White

Read-Host "`n診断完了。何かキーを押してください"