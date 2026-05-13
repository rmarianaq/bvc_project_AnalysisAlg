# Despliegue Simple - BVC Analysis

## 🎯 Opciones de Despliegue

### Opción 1: Docker Local (Probar antes de desplegar)

```bash
# Windows
docker-local.bat

# Linux/Mac
chmod +x deploy-ec2.sh
./deploy-ec2.sh
```

### Opción 2: AWS EC2 con Docker (Recomendado)

**Ventajas:**
- ✅ Todo en un solo servidor
- ✅ PostgreSQL incluido
- ✅ Fácil de mantener
- ✅ ~$19/mes

**Pasos:**
1. Crear EC2 (t2.small, Ubuntu 22.04)
2. Conectar por SSH
3. Ejecutar comandos de instalación
4. Listo

---

## 🚀 Despliegue en EC2 - Paso a Paso

### 1. Crear Instancia EC2

En AWS Console:
- **AMI:** Ubuntu 22.04 LTS
- **Tipo:** t2.small (2 GB RAM)
- **Almacenamiento:** 20 GB
- **Security Group:** Puertos 22, 80, 8000

### 2. Conectar por SSH

```bash
ssh -i tu-clave.pem ubuntu@tu-ip-publica
```

### 3. Instalar Docker (Copiar y pegar todo)

```bash
# Actualizar sistema
sudo apt-get update && sudo apt-get upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Instalar Docker Compose
sudo apt-get install docker-compose-plugin -y

# Instalar Git
sudo apt-get install git -y

# Verificar
docker --version
docker compose version
```

### 4. Clonar y Configurar

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/bvc_project_AnalysisAlg.git
cd bvc_project_AnalysisAlg

# Crear archivo .env
cat > .env << EOF
DB_PASSWORD=tu_password_super_seguro_2026
EOF

# Dar permisos
chmod +x deploy-ec2.sh
```

### 5. Desplegar

```bash
# Ejecutar script de despliegue
./deploy-ec2.sh

# O manualmente
docker compose up -d --build
```

### 6. Verificar

```bash
# Ver estado
docker compose ps

# Ver logs
docker compose logs -f

# Probar API
curl http://localhost:8000/health
```

---

## 🌐 Acceder desde Internet

### Desde tu navegador:

```
http://TU_IP_PUBLICA:8000/docs
```

Reemplaza `TU_IP_PUBLICA` con la IP de tu EC2.

---

## 📱 Configurar Frontend

### Opción A: Nginx en la misma EC2

```bash
# Instalar Nginx
sudo apt-get install nginx -y

# Construir frontend
cd frontend
npm install
npm run build

# Copiar a Nginx
sudo cp -r build/* /var/www/html/

# Configurar proxy
sudo nano /etc/nginx/sites-available/default
```

Agregar:

```nginx
location /api/ {
    proxy_pass http://localhost:8000/;
}
```

```bash
# Reiniciar Nginx
sudo systemctl restart nginx
```

Acceder: `http://TU_IP_PUBLICA`

### Opción B: Vercel (Más fácil)

1. Sube el frontend a GitHub
2. Conecta con Vercel
3. Configura variable de entorno:
   ```
   REACT_APP_API_URL=http://TU_IP_EC2:8000
   ```

---

## 🔧 Comandos Útiles

### Ver logs:
```bash
docker compose logs -f
```

### Reiniciar:
```bash
docker compose restart
```

### Detener:
```bash
docker compose down
```

### Actualizar código:
```bash
git pull
docker compose up -d --build
```

### Backup de base de datos:
```bash
docker compose exec postgres pg_dump -U postgres bvc_analysis > backup.sql
```

---

## 💰 Costos

- **EC2 t2.small:** ~$17/mes
- **Almacenamiento 20GB:** ~$2/mes
- **Total:** ~$19/mes

---

## ✅ Checklist

- [ ] Crear EC2
- [ ] Abrir puertos (22, 80, 8000)
- [ ] Conectar SSH
- [ ] Instalar Docker
- [ ] Clonar repo
- [ ] Configurar .env
- [ ] Ejecutar deploy-ec2.sh
- [ ] Verificar http://IP:8000/health
- [ ] Configurar frontend

---

## 🆘 Problemas Comunes

### "Cannot connect to database"
```bash
docker compose logs postgres
docker compose restart postgres
```

### "Port already in use"
```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

### Backend no responde
```bash
docker compose logs backend
docker compose restart backend
```

---

## 📚 Documentación Completa

Ver `DESPLIEGUE_EC2.md` para guía detallada.

---

**Universidad del Quindío**  
**Análisis de Algoritmos - 2026**
