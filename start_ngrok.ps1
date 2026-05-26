param(
    [int]$Port = 8001
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$NgrokOutLog = Join-Path $Root "backend\ngrok.out.log"
$NgrokErrLog = Join-Path $Root "backend\ngrok.err.log"
$ConfigScript = Join-Path $Root "set_api_url.ps1"
$BackendScript = Join-Path $Root "run_backend.ps1"
$Npx = (Get-Command npx.cmd -ErrorAction SilentlyContinue).Source
if (-not $Npx) {
    $Npx = (Get-Command npx -ErrorAction Stop).Source
}

& $BackendScript
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

try {
    $tunnels = Invoke-RestMethod -UseBasicParsing "http://127.0.0.1:4040/api/tunnels" -TimeoutSec 2
    $existing = $tunnels.tunnels | Where-Object { $_.proto -eq "https" } | Select-Object -First 1
    if ($existing.public_url) {
        & $ConfigScript -Url $existing.public_url
        Write-Host "ngrok already running: $($existing.public_url)"
        exit 0
    }
} catch {
    # No ngrok API yet.
}

Start-Process `
    -FilePath $Npx `
    -ArgumentList @("ngrok", "http", "$Port") `
    -WorkingDirectory $Root `
    -WindowStyle Hidden `
    -RedirectStandardOutput $NgrokOutLog `
    -RedirectStandardError $NgrokErrLog

for ($i = 0; $i -lt 60; $i++) {
    Start-Sleep -Seconds 1
    try {
        $tunnels = Invoke-RestMethod -UseBasicParsing "http://127.0.0.1:4040/api/tunnels" -TimeoutSec 2
        $httpsTunnel = $tunnels.tunnels | Where-Object { $_.proto -eq "https" } | Select-Object -First 1
        if ($httpsTunnel.public_url) {
            & $ConfigScript -Url $httpsTunnel.public_url
            Write-Host "ngrok running: $($httpsTunnel.public_url)"
            Write-Host "Backend health: $($httpsTunnel.public_url)/health"
            exit 0
        }
    } catch {
        # Keep waiting for ngrok startup.
    }
}

Write-Host "ngrok did not publish a tunnel."
Write-Host "Error log: $NgrokErrLog"
exit 1
