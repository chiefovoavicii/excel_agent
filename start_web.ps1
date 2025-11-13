# Start Web Application
# Usage: .\start_web.ps1

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Data Analyzer - Web UI Launcher" -ForegroundColor Cyan
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
    Write-Host "[WARNING] .env file not found" -ForegroundColor Yellow
    Write-Host "Please rename .env.example to .env and configure API keys" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit
    }
}

Write-Host ""
Write-Host "Starting Streamlit application..." -ForegroundColor Cyan
Write-Host ""

# Start Streamlit
streamlit run app.py
