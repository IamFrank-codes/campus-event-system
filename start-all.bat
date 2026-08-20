@echo off
setlocal EnableExtensions

REM Campus Event System - Windows setup and launcher
REM This script intentionally uses forward slashes in project paths.
set "ROOT=%~dp0"

call :setup_service "user-service"
if errorlevel 1 goto :failed
call :setup_service "event-service"
if errorlevel 1 goto :failed
call :setup_service "booking-service"
if errorlevel 1 goto :failed
call :setup_service "notification-service"
if errorlevel 1 goto :failed
call :setup_service "review-services"
if errorlevel 1 goto :failed

echo.
echo All virtual environments and requirements were prepared.
echo Starting all five FastAPI services...
echo.

start "User/Auth Service - 8001" cmd /k "cd /d "%ROOT%/user-service" && call venv/Scripts/activate && uvicorn main:app --reload --port 8001"
start "Event Service - 8002" cmd /k "cd /d "%ROOT%/event-service" && call venv/Scripts/activate && uvicorn main:app --reload --port 8002"
start "Booking Service - 8003" cmd /k "cd /d "%ROOT%/booking-service" && call venv/Scripts/activate && uvicorn main:app --reload --port 8003"
start "Notification Service - 8004" cmd /k "cd /d "%ROOT%/notification-service" && call venv/Scripts/activate && uvicorn main:app --reload --port 8004"
start "Review Service - 8005" cmd /k "cd /d "%ROOT%/review-services" && call venv/Scripts/activate && uvicorn main:app --reload --port 8005"

echo.
echo Services started:
echo   User/Auth:    http://127.0.0.1:8001/docs
echo   Event:        http://127.0.0.1:8002/docs
echo   Booking:      http://127.0.0.1:8003/docs
echo   Notification: http://127.0.0.1:8004/docs
echo   Review:       http://127.0.0.1:8005/docs
exit /b 0

:setup_service
set "SERVICE=%~1"
echo ================================================
echo Preparing %SERVICE%
echo ================================================
cd /d "%ROOT%/%SERVICE%" || exit /b 1

echo [1/5] Directory: %ROOT%/%SERVICE%
if not exist venv (
    echo [2/5] Creating virtual environment: python -m venv venv
    python -m venv venv
    if errorlevel 1 exit /b 1
) else (
    echo [2/5] Virtual environment already exists: venv
)

echo [3/5] Activating: venv/Scripts/activate
call venv/Scripts/activate
if errorlevel 1 exit /b 1

echo [4/5] Upgrading pip: python.exe -m pip install --upgrade pip
python.exe -m pip install --upgrade pip
if errorlevel 1 exit /b 1

echo [5/5] Installing: pip install -r requirements.txt
pip install -r requirements.txt
if errorlevel 1 exit /b 1

call venv/Scripts/deactivate.bat 2>nul
cd /d "%ROOT%" || exit /b 1
exit /b 0

:failed
echo.
echo ERROR: Setup failed. The service was not started.
echo Check the error above, fix the requirements or Python installation, and run start-all.bat again.
pause
exit /b 1
