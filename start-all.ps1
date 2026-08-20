# Campus Event System - start all services on Windows
# Run from the project root. Paths are normalized to forward slashes.
$ErrorActionPreference = 'Stop'
$root = (Split-Path -Parent $MyInvocation.MyCommand.Path).Replace('\', '/')

$services = @(
    @{ Name = 'User/Auth Service'; Folder = 'user-service'; Port = 8001 },
    @{ Name = 'Event Service'; Folder = 'event-service'; Port = 8002 },
    @{ Name = 'Booking Service'; Folder = 'booking-service'; Port = 8003 },
    @{ Name = 'Notification Service'; Folder = 'notification-service'; Port = 8004 },
    @{ Name = 'Review Service'; Folder = 'review-services'; Port = 8005 }
)

foreach ($service in $services) {
    $servicePath = "$root/$($service.Folder)"
    $python = "$servicePath/venv/Scripts/python.exe"

    if (-not (Test-Path $servicePath)) {
        Write-Error "Service folder not found: $servicePath"
    }
    if (-not (Test-Path $python)) {
        Write-Error "Virtual environment not found: $python`nCreate it with: python -m venv $servicePath/venv"
    }

    $command = "Set-Location '$servicePath'; Write-Host '$($service.Name) - port $($service.Port)' -ForegroundColor Cyan; & '$python' -m uvicorn main:app --host 127.0.0.1 --port $($service.Port)"
    Start-Process powershell.exe -ArgumentList @('-NoExit', '-ExecutionPolicy', 'Bypass', '-Command', $command)
    Start-Sleep -Milliseconds 500
}

Write-Host ''
Write-Host 'All five services have been launched in separate PowerShell windows.' -ForegroundColor Green
Write-Host 'Swagger API pages:' -ForegroundColor Yellow
Write-Host '  User/Auth:    http://127.0.0.1:8001/docs'
Write-Host '  Event:        http://127.0.0.1:8002/docs'
Write-Host '  Booking:      http://127.0.0.1:8003/docs'
Write-Host '  Notification: http://127.0.0.1:8004/docs'
Write-Host '  Review:       http://127.0.0.1:8005/docs'
Write-Host 'Health checks:' -ForegroundColor Yellow
Write-Host '  User/Auth:    http://127.0.0.1:8001/health'
Write-Host '  Event:        http://127.0.0.1:8002/health'
Write-Host '  Booking:      http://127.0.0.1:8003/health'
Write-Host '  Notification: http://127.0.0.1:8004/health'
Write-Host '  Review:       http://127.0.0.1:8005/health'
