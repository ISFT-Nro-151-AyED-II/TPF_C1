@echo off
echo ===================================================
echo   COMPILADOR DEL SISTEMA SACA MUELA (PyInstaller)
echo ===================================================
echo.

:: 1. Verificacion de entorno defensiva
pyinstaller --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR CRITICO] PyInstaller no esta reconocido. 
    echo Asegurate de tener tu entorno virtual activado e instalado pyinstaller.
    pause
    exit /B
)

echo [INFO] Iniciando el proceso de empaquetado...
echo [INFO] Inyectando assets y resolviendo dependencias...

:: 2. Ejecucion de PyInstaller
:: --noconfirm: Sobreescribe builds anteriores sin preguntar.
:: --onefile: Empaqueta todo en un solo binario .exe.
:: --windowed: Oculta la consola negra de Windows por detras de la UI grafica.
:: --name: Nombre del archivo de salida.
:: --icon: Ruta al archivo .ico para el ejecutable.
:: --add-data: Copia la carpeta assets dentro del ejecutable (sintaxis Windows = origen;destino)
pyinstaller --noconfirm ^
            --onefile ^
            --windowed ^
            --name "SacaMuela" ^
            --icon "assets\saca_muela_icono.ico" ^
            --add-data "assets;assets" ^
            "src\formulario_odontologico.py"

:: 3. Reubicacion del ejecutable
echo.
echo [INFO] Moviendo SacaMuela.exe a la raiz del proyecto...
move /Y "dist\SacaMuela.exe" "." >nul

:: 4. Limpieza del entorno
echo [INFO] Purgando carpetas y archivos residuales de compilacion...
rmdir /S /Q "build"
rmdir /S /Q "dist"
del /F /Q "SacaMuela.spec"

echo.
echo ===================================================
echo   [EXITO] Compilacion finalizada. SacaMuela.exe listo.
echo ===================================================
pause
