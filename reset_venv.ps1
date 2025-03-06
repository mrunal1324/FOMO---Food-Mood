# Deactivate virtual environment if active
if (Get-Command deactivate -ErrorAction SilentlyContinue) {
    deactivate
}

# Remove existing virtual environment
if (Test-Path "venv") {
    Remove-Item -Recurse -Force "venv"
}

# Create new virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

Write-Host "Virtual environment has been reset and packages have been installed with compatible versions."
Write-Host "To activate the environment in the future, run: .\venv\Scripts\Activate.ps1"