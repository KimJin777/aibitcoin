@echo off
setlocal enableextensions enabledelayedexpansion

REM 프로젝트 루트로 이동
cd /d "C:\Users\kjink\Documents\gptbitcoin\gptbitcoin"

REM venv 파이썬 경로 설정
set VENV_PY=C:\Users\kjink\Documents\gptbitcoin\gptbitcoin\.venv\Scripts\python.exe

echo [Scheduler] Starting reflection scheduler loop...

:loop
if exist "%VENV_PY%" (
  "%VENV_PY%" scheduler.py
) else (
  python scheduler.py
)

REM 비정상 종료 시 10초 후 재시작
timeout /t 10 /nobreak >nul
goto loop


