@echo off
cd /d "%~dp0"
if not exist "Subir_a_Apps_Script.pyw" (
  echo Falta Subir_a_Apps_Script.pyw en esta carpeta.
  goto :error
)
set PYX=
for %%V in (3.14 3.13 3.12) do (
  if not defined PYX (
    py -%%V -c "import tkinter" >nul 2>nul && set PYX=py -%%V
  )
)
if not defined PYX set PYX=python
echo Usando: %PYX%
%PYX% --version
%PYX% -m pip install --upgrade pyinstaller || goto :error
set ICONO=
if exist "icono.ico" set ICONO=--icon icono.ico
%PYX% -m PyInstaller --onefile --noconsole --noupx --clean %ICONO% --name Subir_a_Apps_Script Subir_a_Apps_Script.pyw || goto :error
echo.
echo Listo: %~dp0dist\Subir_a_Apps_Script.exe
pause
exit /b 0
:error
echo.
echo Algo fallo. Mira el mensaje de arriba.
pause
exit /b 1