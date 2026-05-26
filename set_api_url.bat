@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0set_api_url.ps1" %*
