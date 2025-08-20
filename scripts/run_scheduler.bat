@echo off
setlocal

REM Activate venv if available
set VENV_PY=%~dp0..\venv\Scripts\python.exe

echo [Scheduler] Starting reflection scheduler loop...

if exist "%VENV_PY%" (
  "%VENV_PY%" scheduler.py
) else (
  python scheduler.py
)


