@echo off
setlocal

REM Runs every service test suite using its existing virtual environment.
REM Does not install or upgrade packages.
REM Writes the complete command and pytest output to test-results.md.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0/run-tests-all.ps1"
set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo Markdown evidence file:
echo %~dp0/test-results.md
exit /b %EXIT_CODE%
