# Despliegue del Frontend - BVC Analysis

## 🎯 Dos Opciones Disponibles

### Opción 1: Vercel (RECOMENDADA) ⭐
- **Tiempo:** 2 minutos
- **Costo:** Gratis
- **Dificultad:** Muy fácil
- **HTTPS:** Automático
- **CDN:** Incluido

### Opción 2: Nginx en EC2
- **Tiempo:** 10 minutos
- **Costo:** Incluido en EC2
- **Dificultad:** Media
- **HTTPS:** Manual (opcional)

---

## ⭐ Opción 1: Vercel (RECOMENDADA)

### Paso 1: Preparar el Frontend

Primero, actualiza la configuración del frontend para usar variables de entorno:

```bash
# En tu computadora local
cd frontend/src
```

Edita `App.js` y cambia la URL del API:

```javascript
// Antes:
const API_URL = 'http://localhost:8000';

// Después:
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

### Paso 2: Subir a GitHub

```bash
# Desde la raíz del proyecto
git add .
git commit -m "Preparar frontend para despliegue"
git push origin main
```

### Paso 3: Desplegar en Vercel

1. Ve a [vercel.com](https://vercel.com)
2. Click en "Sign Up" (usa tu cuenta de GitHub)
3. Click en "New Project"
4. Selecciona tu repositorio `bvc_project_AnalysisAlg`
5. Configura:
   - **Framework Preset:** Create React App
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `build`

6. Click en "Environment Variables" y agrega:
   ```
   Name: REACT_APP_API_URL
   Value: http://TU_IP_EC2:8000
   ```
   (Reemplaza `TU_IP_EC2` con la IP pública de tu EC2)

7. Click en "Deploy"

### Paso 4: Configurar CORS en el Backend

En tu EC2, edita el archivo de configuración:

```bash
# Conectar a EC2
ssh -i clave.pem ubuntu@IP_EC2

# Ir al proyecto
cd bvc_project_AnalysisAlg

# Editar main.py
nano backend/app/main.py
```

Busca la sección de CORS y actualiza:

```python
# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://tu-app.vercel.app",  # Agregar tu URL de Vercel
        "https://*.vercel.app"  # Permitir todos los subdominios de Vercel
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Reiniciar backend:

```bash
docker compose restart backend
```

### Paso 5: ¡Listo!

Tu frontend estará disponible en:
```
https://tu-app.vercel.app
```

---

## 🖥️ Opción 2: Nginx en EC2

### Paso 1: Instalar Node.js y Nginx

```bash
# Conectar a EC2
ssh -i clave.pem ubuntu@IP_EC2

# Instalar Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verificar
node --version
npm --version

# Instalar Nginx
sudo apt-get install -y nginx
```

### Paso 2: Construir el Frontend

```bash
# Ir al proyecto
cd bvc_project_AnalysisAlg/frontend

# Actualizar la URL del API
nano src/App.js
```

Cambiar:
```javascript
const API_URL = 'http://localhost:8000';
```

Por:
```javascript
const API_URL = window.location.origin + '/api';
```

Guardar y construir:

```bash
# Instalar dependencias
npm install

# Construir para producción
npm run build
```

### Paso 3: Configurar Nginx

```bash
# Limpiar directorio web
sudo rm -rf /var/www/html/*

# Copiar build del frontend
sudo cp -r build/* /var/www/html/

# Configurar Nginx
sudo nano /etc/nginx/sites-available/default
```

Reemplazar todo el contenido con:

```nginx
server {
    listen 80;
    server_name _;

    # Frontend
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
```

Guardar y reiniciar Nginx:

```bash
# Verificar configuración
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx

# Verificar estado
sudo systemctl status nginx
```

### Paso 4: Actualizar CORS en Backend

```bash
cd ~/bvc_project_AnalysisAlg

# Editar main.py
nano backend/app/main.py
```

Actualizar CORS:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar tu dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Reiniciar backend:

```bash
docker compose restart backend
```

### Paso 5: Verificar

Accede a:
```
http://TU_IP_EC2
```

El frontend debería cargar y conectarse al backend automáticamente.

---

## 🔄 Actualizar el Frontend

### Con Vercel (Automático)

```bash
# En tu computadora local
git add .
git commit -m "Actualizar frontend"
git push origin main

# Vercel despliega automáticamente
```

### Con Nginx (Manual)

```bash
# En EC2
cd ~/bvc_project_AnalysisAlg/frontend

# Actualizar código
git pull

# Reconstruir
npm run build

# Copiar a Nginx
sudo rm -rf /var/www/html/*
sudo cp -r build/* /var/www/html/

# Limpiar caché del navegador
```

---

## 🆚 Comparación

| Característica | Vercel | Nginx en EC2 |
|----------------|--------|--------------|
| **Costo** | Gratis | Incluido en EC2 |
| **Configuración** | 2 minutos | 10 minutos |
| **HTTPS** | Automático | Manual |
| **CDN** | Incluido | No |
| **Deploy** | Automático | Manual |
| **Velocidad** | Muy rápido | Depende de EC2 |
| **Mantenimiento** | Cero | Medio |

---

## 💡 Recomendación

### Para Desarrollo/Pruebas:
→ **Nginx en EC2** (todo en un lugar)

### Para Producción:
→ **Vercel** (más profesional, más rápido, más fácil)

---

## 🔒 Configurar HTTPS (Solo para Nginx)

Si usas Nginx y quieres HTTPS:

```bash
# Instalar Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtener certificado (necesitas un dominio)
sudo certbot --nginx -d tu-dominio.com

# Renovación automática
sudo certbot renew --dry-run
```

---

## 🐛 Solución de Problemas

### Frontend no conecta con Backend

**Vercel:**
```bash
# Verificar variable de entorno en Vercel
REACT_APP_API_URL=http://TU_IP_EC2:8000

# Verificar CORS en backend
# Debe incluir tu URL de Vercel
```

**Nginx:**
```bash
# Ver logs de Nginx
sudo tail -f /var/log/nginx/error.log

# Verificar proxy
curl http://localhost/api/health
```

### Error de CORS

```bash
# En EC2, editar main.py
nano backend/app/main.py

# Agregar tu dominio a allow_origins
allow_origins=["https://tu-app.vercel.app"]

# Reiniciar
docker compose restart backend
```

### Nginx no inicia

```bash
# Ver error
sudo nginx -t

# Ver logs
sudo journalctl -u nginx -n 50
```

---

## ✅ Checklist

### Vercel
- [ ] Frontend actualizado con variables de entorno
- [ ] Código subido a GitHub
- [ ] Proyecto creado en Vercel
- [ ] Variable `REACT_APP_API_URL` configurada
- [ ] Deploy exitoso
- [ ] CORS configurado en backend
- [ ] Frontend conecta con backend

### Nginx
- [ ] Node.js instalado
- [ ] Nginx instalado
- [ ] Frontend construido
- [ ] Archivos copiados a `/var/www/html/`
- [ ] Nginx configurado con proxy
- [ ] Nginx reiniciado
- [ ] CORS configurado en backend
- [ ] Frontend accesible

---

## 🎯 URLs Finales

### Con Vercel:
- **Frontend:** `https://tu-app.vercel.app`
- **Backend:** `http://TU_IP_EC2:8000`

### Con Nginx:
- **Frontend:** `http://TU_IP_EC2`
- **Backend:** `http://TU_IP_EC2/api`

---

**Universidad del Quindío**  
**Análisis de Algoritmos - 2026**  
**Despliegue de Frontend**
