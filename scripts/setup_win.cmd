
@echo off
if not exist .venv (
    python -m venv .venv
)
call .venv\Scriptsctivate
pip install --upgrade pip
pip install -r requirements.txt
echo [OK] Virtual environment ready.
