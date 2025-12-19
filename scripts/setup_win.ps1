
Param([string]$Kid = "2025-12-KEY-01")
if (!(Test-Path .venv)) { python -m venv .venv }
. .venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "[OK] venv ready."
