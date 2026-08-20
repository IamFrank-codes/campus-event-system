@echo off
setlocal EnableExtensions

REM Run each service test suite with that service's own virtual environment.
REM Do not run pytest from the project root because every folder contains test_main.py.
set "ROOT=%~dp0"
set "FAILED=0"

call :run_tests "user-service"
call :run_tests "event-service"
call :run_tests "booking-service"
call :run_tests "notification-service"
call :run_tests "review-services"

if "%FAILED%"=="0" (
    echo.
    echo All service test commands completed successfully.
    exit /b 0
)

echo.
echo One or more service test suites failed. Review the output above.
exit /b 1

:run_tests
set "SERVICE=%~1"
set "PYTHON=%ROOT%/%SERVICE%/venv/Scripts/python.exe"

echo.
echo ==================================================
echo Running tests for %SERVICE%
echo ==================================================
if not exist "%PYTHON%" (
    echo ERROR: Missing virtual environment interpreter: %PYTHON%
    echo Run start-all.bat first, or create it with:
    echo cd %ROOT%/%SERVICE%/
    echo python -m venv venv
    echo venv/Scripts/activate
    echo python.exe -m pip install --upgrade pip
    echo pip install -r requirements.txt
    set "FAILED=1"
    exit /b 0
)

"%PYTHON%" -m pip install -r "%ROOT%/%SERVICE%/requirements.txt"
if errorlevel 1 (
    echo ERROR: Dependency installation failed for %SERVICE%
    set "FAILED=1"
    exit /b 0
)

cd /d "%ROOT%/%SERVICE%" || (
    set "FAILED=1"
    exit /b 0
)
"%PYTHON%" -m pytest -v
if errorlevel 1 set "FAILED=1"
cd /d "%ROOT%" >nul
exit /b 0
