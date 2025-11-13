# Run Test Script
# Usage: .\run_test.ps1

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Data Analyzer - Test Runner" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check virtual environment
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "[OK] Activating virtual environment..." -ForegroundColor Green
    .\venv\Scripts\Activate.ps1
}
else {
    Write-Host "[WARNING] Virtual environment not found, using system Python" -ForegroundColor Yellow
}

# Check .env file
if (Test-Path ".\.env") {
    Write-Host "[OK] Found .env configuration file" -ForegroundColor Green
}
else {
    Write-Host "[ERROR] .env file not found!" -ForegroundColor Red
    Write-Host "Please rename .env.example to .env and configure API keys" -ForegroundColor Yellow
    exit
}

# Check test data
if (Test-Path "D:\ms_project\大模型实习项目测试.csv") {
    Write-Host "[OK] Found test data file" -ForegroundColor Green
}
else {
    Write-Host "[ERROR] Test data file not found!" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "Starting tests..." -ForegroundColor Cyan
Write-Host "Will process 3 related questions sequentially" -ForegroundColor Cyan
Write-Host ""

# Run tests
python test_analyzer.py

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Tests Complete" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
