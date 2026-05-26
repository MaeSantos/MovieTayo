param(
    [string]$Url = ""
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ConfigPath = Join-Path $Root "frontend\api-config.js"
$CleanUrl = $Url.Trim().TrimEnd("/")

if ($CleanUrl -and $CleanUrl -notmatch "^https?://") {
    throw "API URL must start with http:// or https://"
}

$EscapedUrl = $CleanUrl.Replace("\", "\\").Replace('"', '\"')
Set-Content -Path $ConfigPath -Value "window.MOVIETAYO_API_BASE = `"$EscapedUrl`";" -Encoding ASCII

if ($CleanUrl) {
    Write-Host "API URL set to $CleanUrl"
} else {
    Write-Host "API URL cleared. The app will use local fallback URLs."
}
