param(
    [switch]$Ngrok
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendScript = Join-Path $Root "run_backend.ps1"
$NgrokScript = Join-Path $Root "start_ngrok.ps1"
$ConfigScript = Join-Path $Root "set_api_url.ps1"
$Adb = Join-Path $env:LOCALAPPDATA "Android\Sdk\platform-tools\adb.exe"
$AndroidRoot = Join-Path $Root "android"
$DebugApk = Join-Path $AndroidRoot "app\build\outputs\apk\debug\app-debug.apk"
$GradleWrapper = Join-Path $AndroidRoot "gradlew.bat"
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

if (Test-Path $Adb) {
    try {
        $devices = & $Adb devices
        $hasDevice = $devices | Where-Object { $_ -match "`tdevice$" } | Select-Object -First 1
        if (-not $hasDevice) {
            Write-Host "Backend is ready. Android launch skipped: no connected device."
            Write-Host "Desktop frontend: $Root\frontend\index.html"
            exit 0
        }

        if ($Ngrok) {
            if (-not $Gradle) {
                throw "No Gradle executable found. Expected android\gradlew.bat or $UserGradle"
            }

            $env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr"
            Push-Location $AndroidRoot
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

        & $Adb shell am start -n com.mae.movieapp/.MainActivity | Out-Null
        Write-Host "Android app launched."
    } catch {
        Write-Host "Backend is ready. Android launch skipped: $($_.Exception.Message)"
    }
}

Write-Host "Desktop frontend: $Root\frontend\index.html"
