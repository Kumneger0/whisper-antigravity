# Whisper Antigravity Windows Installer (PowerShell)
# Usage:
#   irm https://raw.githubusercontent.com/Kumneger0/whisper-antigravity/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

$RepoUrl = "https://github.com/Kumneger0/whisper-antigravity.git"
$InstallDir = Join-Path $env:USERPROFILE ".local\share\whisper-antigravity"
$BinDir = Join-Path $env:USERPROFILE ".local\bin"

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "        Installing Whisper Antigravity (Windows)       " -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan

# 1. Detect Python
$PythonCmd = $null
if (Get-Command "python" -ErrorAction SilentlyContinue) {
    $PythonCmd = "python"
} elseif (Get-Command "py" -ErrorAction SilentlyContinue) {
    $PythonCmd = "py"
} else {
    Write-Error "Python 3 is required but not found in PATH. Please install Python 3.9+ from python.org or Microsoft Store."
}

$PyVer = & $PythonCmd --version
Write-Host "Using Python: $PyVer" -ForegroundColor Green

# 2. Check or Sync Repository
$ScriptDir = $PSScriptRoot
if ($ScriptDir -and (Test-Path (Join-Path $ScriptDir "pyproject.toml"))) {
    Write-Host "Installing from local checkout..." -ForegroundColor Yellow
    if (!(Test-Path $InstallDir)) {
        New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    }
    Copy-Item -Path "$ScriptDir\*" -Destination $InstallDir -Recurse -Force -Exclude ".venv", "__pycache__", ".git"
} else {
    if (Test-Path "$InstallDir\.git") {
        Write-Host "Updating existing installation in $InstallDir..." -ForegroundColor Yellow
        git -C $InstallDir pull --quiet
    } else {
        Write-Host "Cloning whisper-antigravity into $InstallDir..." -ForegroundColor Yellow
        if (Test-Path $InstallDir) {
            Remove-Item -Path $InstallDir -Recurse -Force
        }
        New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
        git clone --depth 1 $RepoUrl $InstallDir --quiet
    }
}

# 3. Create Python Virtual Environment
$VenvDir = Join-Path $InstallDir ".venv"
$VenvPy = Join-Path $VenvDir "Scripts\python.exe"
$VenvPip = Join-Path $VenvDir "Scripts\pip.exe"

if (!(Test-Path $VenvDir)) {
    Write-Host "Creating virtual environment at $VenvDir..." -ForegroundColor Yellow
    & $PythonCmd -m venv $VenvDir
}

Write-Host "Installing dependencies with pip..." -ForegroundColor Yellow
& $VenvPip install -q --upgrade pip
& $VenvPip install -q -e $InstallDir

# 4. Create Batch Wrapper in ~/.local/bin
if (!(Test-Path $BinDir)) {
    New-Item -ItemType Directory -Path $BinDir -Force | Out-Null
}

$BatPath = Join-Path $BinDir "whisper-antigravity.cmd"
$BatContent = "@echo off`r`n`"$VenvDir\Scripts\whisper-antigravity.exe`" %*"
Set-Content -Path $BatPath -Value $BatContent -Encoding ASCII
Write-Host "Created CLI wrapper at $BatPath" -ForegroundColor Green

# 5. Check PATH and optionally guide user
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -notlike "*$BinDir*") {
    Write-Host "`nNotice: $BinDir is not in your User PATH." -ForegroundColor Yellow
    Write-Host "To add it permanently, run in PowerShell:" -ForegroundColor Yellow
    Write-Host "  [Environment]::SetEnvironmentVariable('Path', `$env:Path + ';$BinDir', 'User')" -ForegroundColor Cyan
}

# 6. Register Global Hook and Rule in Antigravity
Write-Host "`nRegistering Antigravity global hook and rule..." -ForegroundColor Yellow
& $VenvPy -m whisper_antigravity.cli install --global

Write-Host "`n=======================================================" -ForegroundColor Cyan
Write-Host "  Whisper Antigravity installed successfully!" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "Quick Commands:"
Write-Host "  • Test speech   : whisper-antigravity test"
Write-Host "  • Toggle ON     : whisper-antigravity on"
Write-Host "  • Toggle OFF    : whisper-antigravity off"
Write-Host "  • Status        : whisper-antigravity status"
Write-Host "  • Select Voice  : whisper-antigravity voice"
Write-Host "=======================================================" -ForegroundColor Cyan
