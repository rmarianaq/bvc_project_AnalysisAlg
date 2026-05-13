@echo off
REM ============================================================
REM Script de Configuracion Inicial - BVC Analysis
REM ============================================================

echo.
echo ============================================================
echo CONFIGURACION INICIAL - BVC ANALYSIS
echo ============================================================
echo.

REM Verificar que estamos en el directorio correcto
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

echo [1/7] Verificando entorno virtual de Python...
if not exist "backend\venv" (
    echo ERROR: No se encuentra el entorno virtual
    echo Crea el entorno virtual primero: python -m venv backend\venv
    pause
    exit /b 1
)
echo OK - Entorno virtual encontrado

echo.
echo [2/7] Instalando dependencias de Python...
cd backend
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Fallo la instalacion de dependencias
    pause
    exit /b 1
)
echo OK - Dependencias instaladas

echo.
echo [3/7] Inicializando base de datos...
python -c "from app.core.database import init_db; init_db()"
if errorlevel 1 (
    echo ERROR: Fallo la inicializacion de la base de datos
    echo Verifica que PostgreSQL este corriendo y el archivo .env este configurado
    pause
    exit /b 1
)
echo OK - Base de datos inicializada

echo.
echo [4/7] Descargando datos financieros (esto puede tardar 2-3 minutos)...
python -c "from app.etl.extractor import extract_all_data; extract_all_data()"
if errorlevel 1 (
    echo ERROR: Fallo la descarga de datos
    pause
    exit /b 1
)
echo OK - Datos descargados

echo.
echo [5/7] Creando tablas de cache...
echo NOTA: Debes ejecutar manualmente el archivo create_cache_tables.sql en PostgreSQL
echo       Opcion 1: psql -U postgres -d bvc_analysis -f create_cache_tables.sql
echo       Opcion 2: Usar pgAdmin y ejecutar el script
echo.
pause

echo.
echo [6/7] Pre-calculando datos (esto puede tardar 1-2 minutos)...
python -m app.cache.precompute
if errorlevel 1 (
    echo ERROR: Fallo el pre-calculo de datos
    echo Verifica que las tablas de cache esten creadas
    pause
    exit /b 1
)
echo OK - Datos pre-calculados

cd ..

echo.
echo [7/7] Instalando dependencias de Node.js...
cd frontend
call npm install
if errorlevel 1 (
    echo ERROR: Fallo la instalacion de dependencias de Node.js
    pause
    exit /b 1
)
echo OK - Dependencias de Node.js instaladas

cd ..

echo.
echo ============================================================
echo CONFIGURACION COMPLETADA EXITOSAMENTE
echo ============================================================
echo.
echo Proximos pasos:
echo   1. Abre DOS terminales
echo   2. Terminal 1 - Backend:
echo      cd backend
echo      venv\Scripts\activate
echo      python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo   3. Terminal 2 - Frontend:
echo      cd frontend
echo      npm start
echo.
echo   4. Abre tu navegador en http://localhost:3000
echo.
echo ============================================================
pause
