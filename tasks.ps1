# PubliCast - PowerShell Task Runner
# Usage: .\tasks.ps1 <command>

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "PubliCast - PowerShell Task Runner" -ForegroundColor Cyan
    Write-Host "===================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\tasks.ps1 <command>" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Available commands:" -ForegroundColor Green
    Write-Host "  install       - Install production dependencies"
    Write-Host "  install-dev   - Install development dependencies"
    Write-Host "  test          - Run tests with pytest"
    Write-Host "  test-cov      - Run tests with coverage report"
    Write-Host "  clean         - Remove build artifacts and cache files"
    Write-Host "  run           - Run the application"
    Write-Host "  lint          - Run code linters (flake8, pylint)"
    Write-Host "  format        - Format code with black"
    Write-Host "  format-check  - Check code formatting without changes"
    Write-Host ""
}

function Install-Dependencies {
    Write-Host "Installing production dependencies..." -ForegroundColor Green
    pip install -r requirements.txt
}

function Install-DevDependencies {
    Write-Host "Installing development dependencies..." -ForegroundColor Green
    pip install -r requirements-dev.txt
}

function Run-Tests {
    Write-Host "Running tests..." -ForegroundColor Green
    pytest
}

function Run-TestsWithCoverage {
    Write-Host "Running tests with coverage..." -ForegroundColor Green
    pytest --cov=publi_cast --cov-report=html --cov-report=term
}

function Clean-Project {
    Write-Host "Cleaning project..." -ForegroundColor Green
    
    # Remove build directories
    if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
    if (Test-Path ".pytest_cache") { Remove-Item -Recurse -Force ".pytest_cache" }
    if (Test-Path "htmlcov") { Remove-Item -Recurse -Force "htmlcov" }
    if (Test-Path ".coverage") { Remove-Item -Force ".coverage" }
    
    # Remove egg-info
    Get-ChildItem -Recurse -Filter "*.egg-info" | Remove-Item -Recurse -Force
    
    # Remove __pycache__
    Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
    
    # Remove .pyc files
    Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force
    
    Write-Host "Project cleaned successfully!" -ForegroundColor Green
}

function Run-Application {
    Write-Host "Running PubliCast..." -ForegroundColor Green
    python -m publi_cast.main
}

function Run-Linters {
    Write-Host "Running linters..." -ForegroundColor Green
    Write-Host "Running flake8..." -ForegroundColor Yellow
    flake8 publi_cast/
    Write-Host "Running pylint..." -ForegroundColor Yellow
    pylint publi_cast/
}

function Format-Code {
    Write-Host "Formatting code with black..." -ForegroundColor Green
    black publi_cast/
}

function Check-Format {
    Write-Host "Checking code formatting..." -ForegroundColor Green
    black --check publi_cast/
}

# Command dispatcher
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "install" { Install-Dependencies }
    "install-dev" { Install-DevDependencies }
    "test" { Run-Tests }
    "test-cov" { Run-TestsWithCoverage }
    "clean" { Clean-Project }
    "run" { Run-Application }
    "lint" { Run-Linters }
    "format" { Format-Code }
    "format-check" { Check-Format }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host ""
        Show-Help
    }
}

