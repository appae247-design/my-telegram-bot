# ==============================================
# Setup and run Telegram Bot (PowerShell script)
# ==============================================

# Move to project directory
Set-Location "C:\Users\HP\Desktop\telegram-bot"

# Remove old virtual environment if it exists
if (Test-Path ".venv") {
    Write-Host "Removing old virtual environment..."
    Remove-Item -Recurse -Force ".venv"
}

# Check Python installation
Write-Host "Checking Python installation..."
try {
    python --version
    python -c "import imghdr; print('imghdr module found')"
} catch {
    Write-Host "Python not found or broken. Please install Python 3.13 x64 from python.org and add it to PATH."
    exit
}

# Create new virtual environment
Write-Host "Creating new virtual environment..."
python -m venv ".venv"

# Activate virtual environment
Write-Host "Activating virtual environment..."
$venvActivate = Join-Path ".venv\Scripts" "Activate.ps1"
if (Test-Path $venvActivate) {
    & $venvActivate
} else {
    Write-Host "Activation script not found. Make sure Python created the virtual environment correctly."
    exit
}

# Upgrade pip, setuptools, and wheel
Write-Host "Upgrading pip, setuptools, and wheel..."
python -m pip install --upgrade pip setuptools wheel

# Install python-telegram-bot
Write-Host "Installing python-telegram-bot v13.15..."
pip install python-telegram-bot==13.15

# Automatically set your BOT_TOKEN (replace with your token)
$env:BOT_TOKEN = "8219669072:AAEpflyopAPq3mjZhPoWcprIYWFmN3nTa18"
Write-Host "BOT_TOKEN has been set."

# Run the bot
Write-Host "Starting Telegram bot..."
python bot.py
