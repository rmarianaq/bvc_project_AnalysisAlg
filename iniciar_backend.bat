@echo off
echo ========================================
echo   Iniciando Backend - BVC Analysis
echo ========================================
echo.

cd backend

echo Activando entorno virtual...
call venv\Scripts\activate.bat

echo.
echo ========================================
echo INICIALIZACION AUTOMATICA
echo ========================================
echo.
echo El sistema verificara y creara automaticamente:
echo   - Tablas de base de datos (si no existen)
echo   - Datos financieros (si no existen)
echo   - Cache de datos (si no existe)
echo.
echo Esto puede tardar 2-5 minutos la primera vez.
echo Las siguientes veces sera instantaneo.
echo.
echo ========================================
echo.

echo Iniciando servidor FastAPI en puerto 8000...
echo.
echo API Docs: http://localhost:8000/docs
echo Health Check: http://localhost:8000/health
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
