
@echo off
if "%1"=="" (
    echo Usage: verify_win.cmd ^<pdf_path^>
    exit /b 1
)
set DOC=%1
set PAYLOAD=%DOC:.pdf=.payload.json%
set PK=keys\ed25519_pk.pem
call .venv\Scriptsctivate
python srcerifier.py --doc %DOC% --payload %PAYLOAD% --pk %PK% --rev policyevocations.json --kid 2025-12-KEY-01
