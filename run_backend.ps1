$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendVenvPython = Join-Path $Root "backend\.venv\Scripts\python.exe"
$RootVenvPython = Join-Path $Root ".venv\Scripts\python.exe"
$Python = if (Test-Path $BackendVenvPython) { $BackendVenvPython } elseif (Test-Path $RootVenvPython) { $RootVenvPython } else { $null }
$HealthUrl = "http://127.0.0.1:8001/health"
$RequiredApiUrl = "http://127.0.0.1:8001/api/behavior/stats?user_id=demo"
$OutLog = Join-Path $Root "backend\backend.out.log"
$ErrLog = Join-Path $Root "backend\backend.err.log"
$EnvFile = Join-Path $Root "backend\.env.local"

if (-not $Python) {
    throw "No Python virtualenv found. Expected backend\.venv\Scripts\python.exe or .venv\Scripts\python.exe"
}

if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#") -or -not $line.Contains("=")) {
            return
        }

        $parts = $line.Split("=", 2)
        [Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), "Process")
    }
}

function Test-BackendReady {
    try {
        $health = Invoke-WebRequest -UseBasicParsing $HealthUrl -TimeoutSec 2
        $api = Invoke-WebRequest -UseBasicParsing $RequiredApiUrl -TimeoutSec 2
        return ($health.StatusCode -eq 200 -and $api.StatusCode -eq 200)
    } catch {
        return $false
    }
}

if (Test-BackendReady) {
    Write-Host "Backend already running at $HealthUrl"
    exit 0
}

try {
    $listener = Get-NetTCPConnection -LocalPort 8001 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($listener.OwningProcess) {
        Write-Host "Restarting stale backend process on port 8001..."
        Stop-Process -Id $listener.OwningProcess -Force
        Start-Sleep -Milliseconds 500
    }
} catch {
    # Nothing to restart.
}

Start-Process `
    -FilePath $Python `
    -ArgumentList @("-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8001") `
    -WorkingDirectory $Root `
    -WindowStyle Hidden `
    -RedirectStandardOutput $OutLog `
    -RedirectStandardError $ErrLog

for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Milliseconds 500
    try {
        if (Test-BackendReady) {
            Write-Host "Backend running at $HealthUrl"
            exit 0
        }
    } catch {
        # Keep waiting for startup.
    }
}

Write-Host "Backend failed to answer $HealthUrl"
Write-Host "Error log: $ErrLog"
exit 1
