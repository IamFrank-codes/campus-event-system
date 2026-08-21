@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM Campus Event System - Windows setup and launcher
REM Uses forward-slash paths as requested.
set "ROOT=%~dp0"

for %%S in (user-service event-service booking-service notification-service review-services) do (
    set "SERVICE=%%S"
    echo ================================================
    echo Preparing !SERVICE!
    echo ================================================
    cd /d "%ROOT%!SERVICE!" || (
        echo ERROR: Cannot open !SERVICE!
        pause
        exit /b 1
    )

    echo [1/5] Directory: %ROOT%/!SERVICE!
    if not exist venv (
        echo [2/5] Creating virtual environment: python -m venv venv
        python -m venv venv
        if errorlevel 1 (
            echo ERROR: Could not create the virtual environment for !SERVICE!
            pause
            exit /b 1
        )
    ) else (
        echo [2/5] Virtual environment already exists: venv
    )

    echo [3/5] Activating: venv/Scripts/activate
    call venv/Scripts/activate
    if errorlevel 1 (
        echo ERROR: Could not activate the virtual environment for !SERVICE!
        pause
        exit /b 1
    )

    echo [4/5] Upgrading pip: python.exe -m pip install --upgrade pip
    python.exe -m pip install --upgrade pip
    if errorlevel 1 (
        echo ERROR: Could not upgrade pip for !SERVICE!
        pause
        exit /b 1
    )

    echo [5/5] Installing: pip install -r requirements.txt
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Could not install requirements for !SERVICE!
        pause
        exit /b 1
    )

    call venv/Scripts/deactivate.bat 2>nul
    cd /d "%ROOT%" || exit /b 1
)

echo.
echo All virtual environments and requirements were prepared.
echo Starting all five FastAPI services...
echo.

start "User/Auth Service - 8001" cmd /k "cd /d "%ROOT%/user-service" && call venv/Scripts/activate && python.exe -m uvicorn main:app --reload --port 8001"
start "Event Service - 8002" cmd /k "cd /d "%ROOT%/event-service" && call venv/Scripts/activate && python.exe -m uvicorn main:app --reload --port 8002"
start "Booking Service - 8003" cmd /k "cd /d "%ROOT%/booking-service" && call venv/Scripts/activate && python.exe -m uvicorn main:app --reload --port 8003"
start "Notification Service - 8004" cmd /k "cd /d "%ROOT%/notification-service" && call venv/Scripts/activate && python.exe -m uvicorn main:app --reload --port 8004"
start "Review Service - 8005" cmd /k "cd /d "%ROOT%/review-services" && call venv/Scripts/activate && python.exe -m uvicorn main:app --reload --port 8005"

echo.
echo Services started. Open these Swagger API pages:
echo   User/Auth:    http://127.0.0.1:8001/docs
echo   Event:        http://127.0.0.1:8002/docs
echo   Booking:      http://127.0.0.1:8003/docs
echo   Notification: http://127.0.0.1:8004/docs
echo   Review:       http://127.0.0.1:8005/docs
echo.
echo Health checks, if needed:
echo   User/Auth:    http://127.0.0.1:8001/health
echo   Event:        http://127.0.0.1:8002/health
echo   Booking:      http://127.0.0.1:8003/health
echo   Notification: http://127.0.0.1:8004/health
echo   Review:       http://127.0.0.1:8005/health
pause
