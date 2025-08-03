# setup-helm.ps1
# Run this script as Administrator

Write-Host "=== Helm Setup Script ===" -ForegroundColor Cyan

# Function to install Chocolatey if missing
function Install-Choco {
    Write-Host "Chocolatey not found. Installing..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
}

# Check for Chocolatey
if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
    Install-Choco
} else {
    Write-Host "Chocolatey already installed." -ForegroundColor Green
}

# Refresh environment (so choco is available right away)
$env:Path += ";$([System.Environment]::GetEnvironmentVariable('ChocolateyInstall','Machine'))\bin"

# Install Helm using choco
if (!(choco list --localonly | Select-String -Pattern "^kubernetes-helm")) {
    Write-Host "Installing Helm..." -ForegroundColor Yellow
    choco install kubernetes-helm -y
} else {
    Write-Host "Helm already installed." -ForegroundColor Green
}

# Verify installation
if (Get-Command helm -ErrorAction SilentlyContinue) {
    $helmVersion = helm version --short
    Write-Host "Helm installed successfully: $helmVersion" -ForegroundColor Cyan
} else {
    Write-Host "Helm installation failed. Please restart your terminal and try again." -ForegroundColor Red
}
