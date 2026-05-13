#!/bin/bash

# ============================================================
# Script de Despliegue COMPLETO en EC2 - BVC Analysis
# Backend + Frontend + Nginx - Todo en uno
# ============================================================

echo "============================================================"
echo "🚀 DESPLIEGUE COMPLETO EN EC2 - BVC ANALYSIS"
echo "   Backend + Frontend + Nginx"
echo "============================================================"
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ============================================================
# PASO 1: Verificar Docker
# ============================================================
echo -e "${BLUE}[1/8] Verificando Docker...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no está instalado${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose no está instalado${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker y Docker Compose instalados${NC}"
echo ""

# ============================================================
# PASO 2: Configurar variables de entorno
# ============================================================
echo -e "${BLUE}[2/8] Configurando variables de entorno...${NC}"

if [ ! -f .env ]; then
    cat > .env << EOF
DB_PASSWORD=bvc_secure_password_2026
EOF
    echo -e "${GREEN}✅ Archivo .env creado${NC}"
else
    echo -e "${GREEN}✅ Archivo .env ya existe${NC}"
fi
echo ""

# ============================================================
# PASO 3: Detener contenedores existentes
# ============================================================
echo -e "${BLUE}[3/8] Deteniendo contenedores existentes...${NC}"
docker-compose down
echo -e "${GREEN}✅ Contenedores detenidos${NC}"
echo ""

# ============================================================
# PASO 4: Construir e iniciar backend
# ============================================================
echo -e "${BLUE}[4/8] Construyendo e iniciando backend...${NC}"
docker-compose up -d --build
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backend iniciado${NC}"
else
    echo -e "${RED}❌ Error al iniciar backend${NC}"
    exit 1
fi
echo ""

# ============================================================
# PASO 5: Esperar a que backend esté listo
# ============================================================
echo -e "${BLUE}[5/8] Esperando a que backend esté listo...${NC}"
echo "   (Esto puede tardar 30-60 segundos)"

for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend está listo${NC}"
        break
    fi
    echo "   Intento $i/30..."
    sleep 2
done
echo ""

# ============================================================
# PASO 6: Instalar Node.js y Nginx
# ============================================================
echo -e "${BLUE}[6/8] Instalando Node.js y Nginx...${NC}"

# Verificar si Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "   Instalando Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
    echo -e "${GREEN}✅ Node.js instalado${NC}"
else
    echo -e "${GREEN}✅ Node.js ya está instalado${NC}"
fi

# Verificar si Nginx está instalado
if ! command -v nginx &> /dev/null; then
    echo "   Instalando Nginx..."
    sudo apt-get install -y nginx
    echo -e "${GREEN}✅ Nginx instalado${NC}"
else
    echo -e "${GREEN}✅ Nginx ya está instalado${NC}"
fi
echo ""

# ============================================================
# PASO 7: Construir frontend
# ============================================================
echo -e "${BLUE}[7/8] Construyendo frontend...${NC}"
echo "   (Esto puede tardar 2-3 minutos)"

cd frontend

# Instalar dependencias
if [ ! -d "node_modules" ]; then
    echo "   Instalando dependencias..."
    npm install
fi

# Construir para producción
echo "   Construyendo para producción..."
npm run build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Frontend construido${NC}"
else
    echo -e "${RED}❌ Error al construir frontend${NC}"
    exit 1
fi

cd ..
echo ""

# ============================================================
# PASO 8: Configurar Nginx
# ============================================================
echo -e "${BLUE}[8/8] Configurando Nginx...${NC}"

# Limpiar directorio web
sudo rm -rf /var/www/html/*

# Copiar archivos del frontend
sudo cp -r frontend/build/* /var/www/html/

# Crear configuración de Nginx
sudo tee /etc/nginx/sites-available/default > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;

    # Frontend - React App
    location / {
        root /var/www/html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

# Verificar configuración
sudo nginx -t

if [ $? -eq 0 ]; then
    # Reiniciar Nginx
    sudo systemctl restart nginx
    echo -e "${GREEN}✅ Nginx configurado y reiniciado${NC}"
else
    echo -e "${RED}❌ Error en configuración de Nginx${NC}"
    exit 1
fi
echo ""

# ============================================================
# RESUMEN FINAL
# ============================================================
echo ""
echo "============================================================"
echo -e "${GREEN}✅ DESPLIEGUE COMPLETADO EXITOSAMENTE${NC}"
echo "============================================================"
echo ""
echo "📊 Servicios disponibles:"
echo ""
echo "   🌐 Frontend (React):"
echo "      http://$(curl -s ifconfig.me)"
echo "      http://localhost"
echo ""
echo "   🔌 Backend API:"
echo "      http://$(curl -s ifconfig.me):8000"
echo "      http://localhost:8000"
echo ""
echo "   📚 API Docs:"
echo "      http://$(curl -s ifconfig.me):8000/docs"
echo ""
echo "   🗄️  PostgreSQL:"
echo "      localhost:5432"
echo ""
echo "============================================================"
echo ""
echo "📝 Comandos útiles:"
echo ""
echo "   Ver logs backend:"
echo "   docker-compose logs -f backend"
echo ""
echo "   Ver logs Nginx:"
echo "   sudo tail -f /var/log/nginx/error.log"
echo ""
echo "   Reiniciar backend:"
echo "   docker-compose restart backend"
echo ""
echo "   Reiniciar Nginx:"
echo "   sudo systemctl restart nginx"
echo ""
echo "   Ver estado de servicios:"
echo "   docker-compose ps"
echo "   sudo systemctl status nginx"
echo ""
echo "============================================================"
echo ""
echo "🎉 ¡Tu aplicación está lista!"
echo ""
echo "   Abre tu navegador en: http://$(curl -s ifconfig.me)"
echo ""
echo "============================================================"
