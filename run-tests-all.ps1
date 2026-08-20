$ErrorActionPreference = 'Continue'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Report = Join-Path $Root 'test-results.md'
$Services = @(
    @{ Name = 'User/Auth Service'; Folder = 'user-service' },
    @{ Name = 'Event Service'; Folder = 'event-service' },
    @{ Name = 'Booking Service'; Folder = 'booking-service' },
    @{ Name = 'Notification Service'; Folder = 'notification-service' },
    @{ Name = 'Review Service'; Folder = 'review-services' }
)

$allMarkdown = New-Object System.Collections.Generic.List[string]
$allMarkdown.Add('# Campus Event System Test Results')
$allMarkdown.Add('')
$allMarkdown.Add(('Generated: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')))
$allMarkdown.Add('')
$allMarkdown.Add('> This report contains the exact test commands and complete pytest output for every service. Dependencies are not installed by this runner.')
$allMarkdown.Add('')

$results = @()
$totalPassed = 0
$totalFailed = 0
$totalSkipped = 0
$totalWarnings = 0
$overallFailed = $false

foreach ($service in $Services) {
    $folderPath = Join-Path $Root $service.Folder
    $python = Join-Path $folderPath 'venv/Scripts/python.exe'
    $allMarkdown.Add(('## ' + $service.Name))
    $allMarkdown.Add('')
    $allMarkdown.Add(('Working directory: `' + $folderPath + '`'))
    $allMarkdown.Add('')
    $allMarkdown.Add('**Command:**')
    $allMarkdown.Add('')
    $allMarkdown.Add(('```text' + "`n" + $python + ' -m pytest -v' + "`n" + '```'))
    $allMarkdown.Add('')

    if (-not (Test-Path $python)) {
        $text = "ERROR: Missing virtual environment interpreter: $python"
        Write-Host $text -ForegroundColor Red
        $allMarkdown.Add('```text')
        $allMarkdown.Add($text)
        $allMarkdown.Add('```')
        $allMarkdown.Add('')
        $results += [pscustomobject]@{ Name=$service.Name; Passed=0; Failed=0; Skipped=0; Warnings=0; Status='MISSING ENVIRONMENT' }
        $overallFailed = $true
        continue
    }

    Write-Host ''
    Write-Host ('Running tests for ' + $service.Name) -ForegroundColor Cyan
    Push-Location $folderPath
    $output = @(& $python -m pytest -v 2>&1 | ForEach-Object { $_.ToString() })
    $exitCode = $LASTEXITCODE
    Pop-Location
    $output | ForEach-Object { Write-Host $_ }

    $allMarkdown.Add('```text')
    $output | ForEach-Object { $allMarkdown.Add($_) }
    $allMarkdown.Add('```')
    $allMarkdown.Add('')

    $summary = ($output | Where-Object { $_ -match '\d+ passed|\d+ failed|\d+ warning|\d+ warnings' } | Select-Object -Last 1)
    $passed = 0; $failed = 0; $skipped = 0; $warnings = 0
    if ($summary -match '(?<n>\d+) passed') { $passed = [int]$Matches['n'] }
    if ($summary -match '(?<n>\d+) failed') { $failed = [int]$Matches['n'] }
    if ($summary -match '(?<n>\d+) skipped') { $skipped = [int]$Matches['n'] }
    if ($summary -match '(?<n>\d+) warnings?') { $warnings = [int]$Matches['n'] }
    if ($exitCode -ne 0) { $overallFailed = $true }
    $totalPassed += $passed
    $totalFailed += $failed
    $totalSkipped += $skipped
    $totalWarnings += $warnings
    $status = if ($exitCode -eq 0) { 'PASSED' } else { 'FAILED' }
    $results += [pscustomobject]@{ Name=$service.Name; Passed=$passed; Failed=$failed; Skipped=$skipped; Warnings=$warnings; Status=$status }
}

$allMarkdown.Add('## Summary')
$allMarkdown.Add('')
$allMarkdown.Add('| Service | Passed | Failed | Skipped | Warnings | Status |')
$allMarkdown.Add('|---|---:|---:|---:|---:|---|')
foreach ($result in $results) {
    $allMarkdown.Add("| $($result.Name) | $($result.Passed) | $($result.Failed) | $($result.Skipped) | $($result.Warnings) | $($result.Status) |")
}
$allMarkdown.Add('')
$allMarkdown.Add('```text')
$allMarkdown.Add(('User/Auth Service:     ' + $results[0].Passed + ' passed'))
$allMarkdown.Add(('Event Service:         ' + $results[1].Passed + ' passed'))
$allMarkdown.Add(('Booking Service:      ' + $results[2].Passed + ' passed'))
$allMarkdown.Add(('Notification Service: ' + $results[3].Passed + ' passed'))
$allMarkdown.Add(('Review Service:       ' + $results[4].Passed + ' passed'))
$allMarkdown.Add('--------------------------------')
$allMarkdown.Add(('Total:                ' + $totalPassed + ' passed'))
$allMarkdown.Add(('Warnings:             ' + $totalWarnings))
$allMarkdown.Add('```')
$allMarkdown.Add('')
$allMarkdown.Add(('Failed tests: ' + $totalFailed))
$allMarkdown.Add(('Skipped tests: ' + $totalSkipped))

$allMarkdown | Set-Content -Path $Report -Encoding UTF8
Write-Host ''
Write-Host 'Markdown report saved to:' -ForegroundColor Green
Write-Host $Report -ForegroundColor Green
Write-Host ''
Write-Host 'Summary:' -ForegroundColor Green
Write-Host ('User/Auth Service:     ' + $results[0].Passed + ' passed')
Write-Host ('Event Service:         ' + $results[1].Passed + ' passed')
Write-Host ('Booking Service:      ' + $results[2].Passed + ' passed')
Write-Host ('Notification Service: ' + $results[3].Passed + ' passed')
Write-Host ('Review Service:       ' + $results[4].Passed + ' passed')
Write-Host '--------------------------------'
Write-Host ('Total:                ' + $totalPassed + ' passed')
Write-Host ('Warnings:             ' + $totalWarnings)
if ($overallFailed) { exit 1 } else { exit 0 }
