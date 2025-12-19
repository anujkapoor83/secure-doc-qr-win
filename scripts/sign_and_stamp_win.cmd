
@echo off
if "%1"=="" (
    echo Usage: sign_and_stamp_win.cmd ^<pdf_path^> [issuer] [kid]
    exit /b 1
)
set DOC=%1
set ISSUER=%2
if "%ISSUER%"=="" set ISSUER=OPTUM-UHCT
set KID=%3
if "%KID%"=="" set KID=2025-12-KEY-01

call .venv\Scriptsctivate
if not exist keys\ed25519_sk.pem (
    python src\scripts\genkey.py --out keys\ed25519_sk.pem --pub keys\ed25519_pk.pem --kid %KID%
)
python src\generator.py --doc %DOC% --issuer %ISSUER% --kid %KID% --sk keys\ed25519_sk.pem --stamp
