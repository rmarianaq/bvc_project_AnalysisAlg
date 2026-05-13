#!/bin/bash

# ============================================================
# Script de Despliegue en EC2 - BVC Analysis
# ============================================================

echo "============================================================"
echo "🚀 DESPLIEGUE EN EC2 - BVC ANALYSIS"
echo "============================================================"
echo ""

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar que Docker esté instalado
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no está instalado${NC}"
    echo "Instalar con: curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh"
    exit 1
fi

# Verificar que Docker Compose esté instalado
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose no está instalado${NC}"
    echo "Instalar con: sudo apt-get install docker-compose-plugin"
    exit 1
fi

echo -e "${GREEN}✅ Docker y Docker Compose instalados${NC}"
echo ""

# Paso 1: Configurar variables de entorno
echo -e "${BLUE}[1/6] Configurando variables de entorno...${NC}"

if [ ! -f .env ]; then
    echo "Creando archivo .env..."
    cat > .env << EOF
# Base de datos
DB_PASSWORD=bvc_secure_password_2026

# Cambiar en producción
# DB_PASSWORD=tu_password_super_seguro_aqui
EOF
    echo -e "${GREEN}✅ Archivo .env creado${NC}"
else
    echo -e "${GREEN}✅ Archivo .env ya existe${NC}"
fi

# Paso 2: Detener contenedores existentes
echo ""
echo -e "${BLUE}[2/6] Deteniendo contenedores existentes...${NC}"
docker-compose down
echo -e "${GREEN}✅ Contenedores detenidos${NC}"

# Paso 3: Construir imágenes
echo ""
echo -e "${BLUE}[3/6] Construyendo imágenes Docker...${NC}"
docker-compose build --no-cache
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Imágenes construidas${NC}"
else
    echo -e "${RED}❌ Error al construir imágenes${NC}"
    exit 1
fi

# Paso 4: Iniciar servicios
echo ""
echo -e "${BLUE}[4/6] Iniciando servicios...${NC}"
docker-compose up -d
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Servicios iniciados${NC}"
else
    echo -e "${RED}❌ Error al iniciar servicios${NC}"
    exit 1
fi

# Paso 5: Esperar a que los servicios estén listos
echo ""
echo -e "${BLUE}[5/6] Esperando a que los servicios estén listos...${NC}"
echo "Esto puede tardar 30-60 segundos..."

# Esperar a PostgreSQL
echo "Esperando a PostgreSQL..."
sleep 10

# Esperar a Backend
echo "Esperando a Backend..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend está listo${NC}"
        break
    fi
    echo "Intento $i/30..."
    sleep 2
done

# Paso 6: Verificar estado
echo ""
echo -e "${BLUE}[6/6] Verificando estado de los servicios...${NC}"
docker-compose ps

echo ""
echo "============================================================"
echo -e "${GREEN}✅ DESPLIEGUE COMPLETADO${NC}"
echo "============================================================"
echo ""
echo "📊 Servicios disponibles:"
echo "   • Backend API: http://localhost:8000"
echo "   • API Docs: http://localhost:8000/docs"
echo "   • Health Check: http://localhost:8000/health"
echo "   • PostgreSQL: localhost:5432"
echo ""
echo "📝 Comandos útiles:"
echo "   • Ver logs: docker-compose logs -f"
echo "   • Ver logs backend: docker-compose logs -f backend"
echo "   • Ver logs postgres: docker-compose logs -f postgres"
echo "   • Detener: docker-compose down"
echo "   • Reiniciar: docker-compose restart"
echo ""
echo "🔧 Configuración:"
echo "   • Editar .env para cambiar contraseñas"
echo "   • Los datos se guardan en volumen Docker (persisten)"
echo ""
echo "============================================================"
