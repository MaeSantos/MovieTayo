@echo off
if /I "%~1"=="ngrok" (
  powershell -ExecutionPolicy Bypass -File "%~dp0start_app.ps1" -Ngrok
) else (
  powershell -ExecutionPolicy Bypass -File "%~dp0start_app.ps1"
)
