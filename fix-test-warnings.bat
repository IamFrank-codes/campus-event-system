@echo off
setlocal EnableExtensions

REM One-time repair for Starlette/httpx test-client warnings.
REM This is separate from run-tests-all.bat, which never installs packages.
set "ROOT=%~dp0"
set "FAILED=0"

call :install_httpx2 "user-service"
call :install_httpx2 "event-service"
call :install_httpx2 "booking-service"
call :install_httpx2 "notification-service"
call :install_httpx2 "review-services"

if "%FAILED%"=="0" (
    echo.
    echo httpx2 was installed in all available service environments.
    echo Now run: run-tests-all.bat
    exit /b 0
)

echo.
echo One or more environments could not be updated.
exit /b 1

:install_httpx2
set "SERVICE=%~1"
set "PYTHON=%ROOT%/%SERVICE%/venv/Scripts/python.exe"
echo.
echo Updating %SERVICE%
if not exist "%PYTHON%" (
    echo ERROR: Missing virtual environment: %PYTHON%
    set "FAILED=1"
    exit /b 0
)
"%PYTHON%" -m pip install --upgrade "httpx2==2.12.0"
if errorlevel 1 set "FAILED=1"
exit /b 0
