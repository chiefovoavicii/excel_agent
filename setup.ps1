# Setup Script - Install all dependencies
# Usage: .\setup.ps1

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Data Analyzer Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python
Write-Host "Step 1/5: Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 2: Create virtual environment
Write-Host "Step 2/5: Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path ".\venv") {
    Write-Host "[WARNING] Virtual environment already exists" -ForegroundColor Yellow
    $recreate = Read-Host "Recreate? (y/n)"
    if ($recreate -eq "y") {
        Remove-Item -Recurse -Force .\venv
        python -m venv venv
        Write-Host "[OK] Virtual environment recreated" -ForegroundColor Green
    }
}
else {
    python -m venv venv
    Write-Host "[OK] Virtual environment created" -ForegroundColor Green
}

Write-Host ""

# Step 3: Install dependencies
Write-Host "Step 3/5: Installing dependencies..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Gray

.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip -q

# Install requirements
pip install -r requirements.txt -q

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Dependencies installed" -ForegroundColor Green
}
else {
    Write-Host "[ERROR] Failed to install dependencies" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 4: Configure .env file
Write-Host "Step 4/5: Configuring environment..." -ForegroundColor Yellow
if (Test-Path ".\.env") {
    Write-Host "[OK] .env file exists" -ForegroundColor Green
}
else {
    if (Test-Path ".\.env.example") {
        Copy-Item .\.env.example .\.env
        Write-Host "[OK] .env file created from .env.example" -ForegroundColor Green
        Write-Host "[WARNING] Please edit .env file and add your API keys" -ForegroundColor Yellow
    }
    else {
        Write-Host "[WARNING] .env.example not found" -ForegroundColor Yellow
    }
}

Write-Host ""

# Step 5: Check test data
Write-Host "Step 5/5: Checking test data..." -ForegroundColor Yellow
if (Test-Path ".\大模型实习项目测试.csv") {
    Write-Host "[OK] Test data file found" -ForegroundColor Green
}
else {
    Write-Host "[WARNING] Test data file not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env file and configure API keys" -ForegroundColor White
Write-Host "2. Run .\start_web.ps1 to start Web UI" -ForegroundColor White
Write-Host "   or .\run_test.ps1 to run tests" -ForegroundColor White
Write-Host ""
