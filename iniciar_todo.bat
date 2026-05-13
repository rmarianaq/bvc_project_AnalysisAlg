@echo off
echo ============================================================
echo   BVC ANALYSIS - INICIO COMPLETO
echo ============================================================
echo.
echo Este script iniciara:
echo   1. Backend (FastAPI) en puerto 8000
echo   2. Frontend (React) en puerto 3000
echo.
echo Se abriran DOS ventanas de terminal.
echo NO cierres ninguna ventana mientras uses la aplicacion.
echo.
echo ============================================================
echo.

echo Verificando que estamos en el directorio correcto...
if not exist "backend" (
    echo ERROR: No se encuentra la carpeta backend
    echo Ejecuta este script desde el directorio raiz del proyecto
    pause
    exit /b 1
)

if not exist "frontend" (
    echo ERROR: No se encuentra la carpeta frontend
    echo Ejecuta este script desde el directorio raiz del proyecto
    pause
    exit /b 1
)

echo.
echo [1/2] Iniciando Backend...
echo.
start "BVC Analysis - Backend" cmd /k "iniciar_backend.bat"

echo Esperando 3 segundos para que el backend inicie...
timeout /t 3 /nobreak > nul

echo.
echo [2/2] Iniciando Frontend...
echo.
start "BVC Analysis - Frontend" cmd /k "iniciar_frontend.bat"

echo.
echo ============================================================
echo SISTEMA INICIADO
echo ============================================================
echo.
echo Se han abierto dos ventanas:
echo   1. Backend (puerto 8000)
echo   2. Frontend (puerto 3000)
echo.
echo El navegador se abrira automaticamente en:
echo   http://localhost:3000
echo.
echo Para detener el sistema:
echo   - Cierra ambas ventanas de terminal
echo   - O presiona Ctrl+C en cada ventana
echo.
echo ============================================================
echo.
echo Puedes cerrar esta ventana de forma segura.
echo.
pause
