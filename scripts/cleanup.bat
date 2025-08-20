@echo off
setlocal enabledelayedexpansion

REM Cleanup script: prune old images/logs and analysis JSONs
REM Working directory -> project root
cd /d "%~dp0.."

REM Configurable settings
set IMAGE_DIR=images
set LOG_DIR=logs
set KEEP_IMAGES=50
set LOG_RETENTION_DAYS=14

echo [Cleanup] Starting cleanup...

REM 1) Keep only the newest %KEEP_IMAGES% images
if exist "%IMAGE_DIR%" (
	echo [Cleanup] Pruning images in %IMAGE_DIR% ^(keeping %KEEP_IMAGES% newest^)...
	powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-ChildItem -Path '%IMAGE_DIR%' -File | Sort-Object LastWriteTime -Descending | Select-Object -Skip %KEEP_IMAGES% | Remove-Item -Force -ErrorAction SilentlyContinue"
) else (
	echo [Cleanup] Images directory not found: %IMAGE_DIR%
)

REM 2) Delete logs older than %LOG_RETENTION_DAYS% days
if exist "%LOG_DIR%" (
	echo [Cleanup] Deleting logs older than %LOG_RETENTION_DAYS% days in %LOG_DIR%...
	powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-ChildItem -Path '%LOG_DIR%' -File | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-%LOG_RETENTION_DAYS%) } | Remove-Item -Force -ErrorAction SilentlyContinue"
) else (
	echo [Cleanup] Logs directory not found: %LOG_DIR%
)

REM 3) Delete analysis JSON files at project root
echo [Cleanup] Deleting analysis JSON files in project root...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-ChildItem -Path . -File -Filter '*.json' | Remove-Item -Force -ErrorAction SilentlyContinue"

echo [Cleanup] Done.
endlocal
