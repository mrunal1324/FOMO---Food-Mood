# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

Write-Host "Virtual environment setup complete! To activate the environment in the future, run: .\venv\Scripts\Activate.ps1" 