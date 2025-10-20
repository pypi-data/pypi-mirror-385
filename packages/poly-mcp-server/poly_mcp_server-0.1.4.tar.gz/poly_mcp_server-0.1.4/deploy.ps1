# PyPI Deployment Script
# Loads UV_PUBLISH_TOKEN from .vscode/.env or .env file

Write-Host "Starting PyPI deployment..." -ForegroundColor Green

# Find .env file (prioritize .vscode/.env)
$envFile = if (Test-Path ".vscode\.env") {
    ".vscode\.env"
} elseif (Test-Path ".env") {
    ".env"
} else {
    $null
}

if ($envFile) {
    Write-Host "Loading environment variables from $envFile..." -ForegroundColor Cyan
    
    $envContent = Get-Content $envFile
    foreach ($line in $envContent) {
        if ($line -match '^([^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
            Write-Host "Set environment variable: $key" -ForegroundColor Green
        }
    }
} else {
    Write-Host "Warning: .env file not found. Make sure UV_PUBLISH_TOKEN is set." -ForegroundColor Yellow
}

# Check UV_PUBLISH_TOKEN
if (-not $env:UV_PUBLISH_TOKEN) {
    Write-Host "ERROR: UV_PUBLISH_TOKEN is not set." -ForegroundColor Red
    Write-Host "Please either:" -ForegroundColor Yellow
    Write-Host "1. Add UV_PUBLISH_TOKEN=pypi-... to .vscode\.env" -ForegroundColor Yellow
    Write-Host "2. Set it as environment variable: `$env:UV_PUBLISH_TOKEN='pypi-...'" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Running tests..." -ForegroundColor Cyan
uv run pytest
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Tests failed! Aborting deployment." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Building package..." -ForegroundColor Cyan
uv build
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Publishing to PyPI..." -ForegroundColor Cyan
uv publish
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Publish failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Deployment completed successfully!" -ForegroundColor Green
Write-Host "Check package at: https://pypi.org/project/poly-mcp-server/" -ForegroundColor Cyan
