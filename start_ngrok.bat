@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0start_ngrok.ps1" %*
