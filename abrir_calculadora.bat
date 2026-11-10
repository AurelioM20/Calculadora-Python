@echo off
cd /d "%~dp0"

set "PY=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if exist "%PY%" goto executar

set "PY=python"

:executar
"%PY%" calculadora_ui.py
if errorlevel 1 pause
