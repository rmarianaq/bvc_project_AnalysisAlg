@echo off
echo ========================================
echo   Iniciando Frontend - BVC Analysis
echo ========================================
echo.

cd frontend

echo Verificando dependencias...
if not exist "node_modules\" (
    echo Instalando dependencias de npm...
    call npm install
)

echo.
echo Iniciando servidor de desarrollo React...
echo.
echo Frontend: http://localhost:3000
echo.

call npm start

pause
