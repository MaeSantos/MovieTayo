param(
    [switch]$Ngrok
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendScript = Join-Path $Root "run_backend.ps1"
$NgrokScript = Join-Path $Root "start_ngrok.ps1"
$ConfigScript = Join-Path $Root "set_api_url.ps1"
$Adb = Join-Path $env:LOCALAPPDATA "Android\Sdk\platform-tools\adb.exe"
$AdminRoot = Join-Path $Root "android-admin"
$DebugApk = Join-Path $AdminRoot "app\build\outputs\apk\debug\app-debug.apk"
$GradleWrapper = Join-Path $AdminRoot "gradlew.bat"
$UserGradle = Join-Path $env:USERPROFILE ".gradle\wrapper\dists\gradle-8.14.3-all\10utluxaxniiv4wxiphsi49nj\gradle-8.14.3\bin\gradle.bat"
$Gradle = if (Test-Path $GradleWrapper) { $GradleWrapper } elseif (Test-Path $UserGradle) { $UserGradle } else { $null }

if ($Ngrok) {
    & $NgrokScript
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
    & $BackendScript
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & $ConfigScript -Url ""
}

# Copy admin API config
$AdminApiConfig = Join-Path $AdminRoot "app\src\main\assets\api-config.js"
$FrontendApiConfig = Join-Path $Root "frontend\api-config.js"
if (Test-Path $FrontendApiConfig) {
    Copy-Item $FrontendApiConfig $AdminApiConfig -Force
}

if (Test-Path $Adb) {
    try {
        $devices = & $Adb devices
        $hasDevice = $devices | Where-Object { $_ -match "`tdevice$" } | Select-Object -First 1
        if (-not $hasDevice) {
            Write-Host "Backend is ready. Android admin launch skipped: no connected device."
            Write-Host "Desktop admin: $Root\admin\index.html"
            exit 0
        }

        if ($Ngrok) {
            if (-not $Gradle) {
                throw "No Gradle executable found. Expected android-admin\gradlew.bat or $UserGradle"
            }

            $env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr"
            Push-Location $AdminRoot
            try {
                & $Gradle assembleDebug
                if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
            } finally {
                Pop-Location
            }

            & $Adb install -r $DebugApk | Out-Null
        } else {
            & $Adb reverse tcp:8001 tcp:8001 | Out-Null
        }

        & $Adb shell am start -n com.mae.movieadmin/.MainActivity | Out-Null
        Write-Host "Android admin app launched."
    } catch {
        Write-Host "Backend is ready. Android admin launch skipped: $($_.Exception.Message)"
    }
}

Write-Host "Desktop admin: $Root\admin\index.html"
