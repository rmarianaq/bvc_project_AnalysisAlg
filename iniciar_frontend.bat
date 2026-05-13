@echo off
echo ========================================
echo   Iniciando Frontend - BVC Analysis
echo ========================================
echo.

cd frontend

echo Verificando dependencias...
if not exist "node_modules" (
    echo.
    echo Instalando dependencias de Node.js...
    echo (Esto puede tardar 1-2 minutos la primera vez)
    echo.
    call npm install
    echo.
    echo ========================================
    echo Dependencias instaladas correctamente
    echo ========================================
    echo.
)

echo.
echo Iniciando servidor React en puerto 3000...
echo.
echo Frontend: http://localhost:3000
echo.
echo NOTA: El backend debe estar corriendo en puerto 8000
echo.

call npm start

pause
