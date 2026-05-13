@echo off
echo ============================================================
echo   Despliegue Local con Docker - BVC Analysis
echo ============================================================
echo.

REM Verificar que Docker esté instalado
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker no esta instalado
    echo.
    echo Instalar Docker Desktop desde:
    echo https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo Docker instalado correctamente
echo.

REM Crear archivo .env si no existe
if not exist ".env" (
    echo Creando archivo .env...
    (
        echo # Base de datos
        echo DB_PASSWORD=bvc_secure_password_2026
    ) > .env
    echo Archivo .env creado
    echo.
)

echo ============================================================
echo [1/4] Deteniendo contenedores existentes...
echo ============================================================
docker-compose down
echo.

echo ============================================================
echo [2/4] Construyendo imagenes Docker...
echo ============================================================
echo (Esto puede tardar 2-3 minutos la primera vez)
echo.
docker-compose build
if errorlevel 1 (
    echo ERROR: Fallo la construccion de imagenes
    pause
    exit /b 1
)
echo.

echo ============================================================
echo [3/4] Iniciando servicios...
echo ============================================================
docker-compose up -d
if errorlevel 1 (
    echo ERROR: Fallo al iniciar servicios
    pause
    exit /b 1
)
echo.

echo ============================================================
echo [4/4] Esperando a que los servicios esten listos...
echo ============================================================
echo (Esto puede tardar 30-60 segundos)
echo.
timeout /t 30 /nobreak > nul

echo.
echo ============================================================
echo DESPLIEGUE COMPLETADO
echo ============================================================
echo.
echo Servicios disponibles:
echo   - Backend API: http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo   - Health Check: http://localhost:8000/health
echo   - PostgreSQL: localhost:5432
echo.
echo Comandos utiles:
echo   - Ver logs: docker-compose logs -f
echo   - Detener: docker-compose down
echo   - Reiniciar: docker-compose restart
echo.
echo ============================================================
echo.

REM Abrir navegador
start http://localhost:8000/docs

pause
