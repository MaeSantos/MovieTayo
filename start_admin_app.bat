@echo off
if /I "%~1"=="ngrok" (
  powershell -ExecutionPolicy Bypass -File "%~dp0start_admin_app.ps1" -Ngrok
) else (
  powershell -ExecutionPolicy Bypass -File "%~dp0start_admin_app.ps1"
)
