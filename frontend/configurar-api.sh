#!/bin/bash

# ============================================================
# Script para configurar la URL del API en el frontend
# ============================================================

echo "============================================================"
echo "Configuración de URL del API - Frontend BVC Analysis"
echo "============================================================"
echo ""

# Solicitar URL del API
read -p "Ingresa la URL del backend (ej: http://3.85.123.45:8000): " API_URL

# Validar que no esté vacío
if [ -z "$API_URL" ]; then
    echo "❌ Error: URL no puede estar vacía"
    exit 1
fi

# Crear archivo .env.local
cat > .env.local << EOF
# Configuración del API
REACT_APP_API_URL=$API_URL
EOF

echo ""
echo "✅ Configuración guardada en .env.local"
echo ""
echo "URL del API: $API_URL"
echo ""
echo "Próximos pasos:"
echo "  1. npm install"
echo "  2. npm run build"
echo ""
