@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

set "PY=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if not exist "%PY%" set "PY=python"
for %%i in ("%PY%") do set "SCRIPTS=%%~dpiScripts"

echo Instalando dependencias...
"%PY%" -m pip install --quiet --upgrade "flet==0.86.5" "flet-desktop==0.86.5" "flet-web==0.86.5" pyinstaller
if errorlevel 1 goto erro

echo Gerando o executavel...
"%SCRIPTS%\flet.exe" pack calculadora_ui.py -D -y -n Calculadora -i assets/icone.ico --product-name "Calculadora Científica" --file-description "Calculadora científica em Python (Flet)" --product-version 1.0.0 --file-version 1.0.0.0 --company-name "Aurelio" --copyright "MIT (c) 2026 Aurelio" --distpath dist
if errorlevel 1 goto erro

echo.
echo Pronto: dist\Calculadora\Calculadora.exe
pause
exit /b 0

:erro
echo.
echo Falhou ao gerar o executavel.
pause
exit /b 1
