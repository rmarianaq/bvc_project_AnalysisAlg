# 🚀 Guía de Ejecución Local - BVC Analysis

## Requisitos Previos

- **Python 3.8+** instalado
- **Node.js 14+** y npm instalados
- **Conexión a Internet** (para descargar datos financieros)

## 📋 Pasos para Ejecutar el Proyecto

### ⚡ Inicio Rápido

**Terminal 1 - Backend:**
```powershell
cd A:\Documents\GitHub\bvc_project_AnalysisAlg\backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend (NUEVA terminal):**
```powershell
cd A:\Documents\GitHub\bvc_project_AnalysisAlg\frontend
npm start
```

---

### 1️⃣ Configurar y Ejecutar el Backend

#### Paso a Paso (PowerShell o CMD)

```powershell
# 1. Navegar a la carpeta del backend
cd A:\Documents\GitHub\bvc_project_AnalysisAlg\backend

# 2. Activar el entorno virtual
# En PowerShell:
.\venv\Scripts\Activate.ps1

# En CMD:
venv\Scripts\activate.bat

# 3. Instalar/Actualizar dependencias (solo primera vez o si hay cambios)
pip install --upgrade pip
pip install psycopg2-binary pydantic seaborn pandas --upgrade
pip install fastapi uvicorn python-dotenv requests numpy matplotlib reportlab

# 4. Verificar que todo esté instalado
pip list | findstr "psycopg2 pydantic seaborn fastapi"

# 5. Ejecutar el servidor FastAPI
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Nota para Python 3.13**: Si tienes errores de compilación, usa las versiones precompiladas con `--upgrade` como se muestra arriba.

#### Verificar que el backend está corriendo

Abre tu navegador y ve a:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

Deberías ver:
```json
{
  "status": "healthy",
  "database": "connected",
  "assets_count": 22
}
```

---

### 2️⃣ Configurar y Ejecutar el Frontend

**Abre una NUEVA terminal** (deja el backend corriendo en la primera)

```powershell
# 1. Navegar a la carpeta del frontend
cd A:\Documents\GitHub\bvc_project_AnalysisAlg\frontend

# 2. Instalar dependencias (solo la primera vez o si hay cambios)
npm install

# 3. Iniciar el servidor de desarrollo React
npm start
```

**¿Qué esperar?**
- El proceso de instalación puede tardar 1-2 minutos la primera vez
- El navegador se abrirá automáticamente en **http://localhost:3000**
- Verás el mensaje: `Compiled successfully!`
- Si el puerto 3000 está ocupado, te preguntará si quieres usar otro puerto (responde Y)

**Nota**: Si `npm` no es reconocido, instala Node.js desde https://nodejs.org/

---

## 🎯 Flujo de Prueba Completo

### 1. Dashboard Principal
- Verifica que se muestren los 22 activos
- Comprueba el estado del sistema (verde = OK)
- Intenta descargar el PDF (tarda 2-3 minutos)

### 2. Análisis de Similitud
- Selecciona dos activos diferentes (ej: ECOPETROL vs PFBCOLOM)
- Click en "Comparar Similitud"
- Revisa los 4 algoritmos:
  - Distancia Euclidiana
  - Correlación de Pearson
  - Similitud por Coseno
  - DTW

### 3. Análisis de Volatilidad
- Espera a que cargue (calcula volatilidad de todos los activos)
- Filtra por nivel de riesgo: Conservador, Moderado, Agresivo
- Observa las barras de volatilidad

### 4. Análisis de Patrones
- Selecciona un activo (ej: ECOPETROL)
- Click en "Analizar Patrones"
- Revisa:
  - Días consecutivos al alza
  - Picos de volatilidad

### 5. Matriz de Correlación
- Click en "Calcular Matriz de Correlación"
- Espera 1-2 minutos (calcula 22×22 = 484 correlaciones)
- Haz click en cualquier celda para ver detalles

---

## 🔧 Solución de Problemas

### ❌ Error: "Backend no responde"

**Causa**: El backend no está corriendo o está en otro puerto

**Solución**:
```cmd
# Verifica que el backend esté corriendo
# Deberías ver: INFO:     Uvicorn running on http://0.0.0.0:8000

# Si no está corriendo, ejecuta:
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### ❌ Error: "npm: command not found"

**Causa**: Node.js no está instalado

**Solución**:
1. Descarga Node.js desde https://nodejs.org/
2. Instala la versión LTS
3. Reinicia la terminal
4. Verifica: `node --version` y `npm --version`

### ❌ Error: "Port 3000 already in use"

**Causa**: Otro proceso está usando el puerto 3000

**Solución**:
```cmd
# Opción 1: Usar otro puerto
set PORT=3001 && npm start

# Opción 2: Matar el proceso en el puerto 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### ❌ Error: "CORS policy blocked"

**Causa**: Problema de configuración CORS

**Solución**: El backend ya tiene CORS configurado. Verifica que:
- Backend esté en http://localhost:8000
- Frontend esté en http://localhost:3000

### ❌ Error: "Database connection failed"

**Causa**: La base de datos SQLite no se creó

**Solución**:
```cmd
cd backend
python -c "from app.core.database import init_db; init_db()"
```

### ❌ Error: "No data available"

**Causa**: No se han descargado datos financieros

**Solución**:
```cmd
# Ejecuta el ETL manualmente
cd backend
python -c "from app.etl.extractor import extract_all_data; extract_all_data()"
```

---

## 📊 Endpoints de la API

### Información General
- `GET /health` - Estado del sistema
- `GET /assets` - Lista de activos

### Similitud
- `POST /similarity/compare` - Comparar dos activos
- `GET /similarity/correlation-matrix` - Matriz de correlación

### Volatilidad
- `GET /volatility/all` - Volatilidad de todos los activos
- `GET /volatility/{ticker}` - Volatilidad de un activo

### Patrones
- `GET /patterns/{ticker}` - Patrones de un activo

### Reportes
- `POST /reports/generate-pdf` - Generar reporte PDF

### Ordenamiento
- `POST /sorting/benchmark` - Benchmark de algoritmos

---

## 🎓 Estructura de Ejecución

```
Terminal 1 (Backend):
┌─────────────────────────────────────┐
│ cd backend                          │
│ venv\Scripts\activate               │
│ uvicorn app.main:app --reload      │
│                                     │
│ ✅ Running on http://0.0.0.0:8000  │
└─────────────────────────────────────┘

Terminal 2 (Frontend):
┌─────────────────────────────────────┐
│ cd frontend                         │
│ npm start                           │
│                                     │
│ ✅ Running on http://localhost:3000│
└─────────────────────────────────────┘

Navegador:
┌─────────────────────────────────────┐
│ http://localhost:3000               │
│                                     │
│ 📊 BVC Analysis Dashboard          │
└─────────────────────────────────────┘
```

---

## 📝 Notas Importantes

1. **Orden de ejecución**: Siempre inicia el backend ANTES que el frontend
2. **Primera ejecución**: La primera vez tarda más (descarga datos, crea DB)
3. **Reportes PDF**: Pueden tardar 2-3 minutos en generarse
4. **Matriz de correlación**: Tarda 1-2 minutos (484 cálculos)
5. **Datos en tiempo real**: Se descargan de APIs públicas (Yahoo Finance, BVC)

---

## 🎯 Checklist de Verificación

- [ ] Backend corriendo en puerto 8000
- [ ] Frontend corriendo en puerto 3000
- [ ] Base de datos SQLite creada
- [ ] 22 activos cargados en la base de datos
- [ ] API Docs accesible en /docs
- [ ] Dashboard muestra estadísticas
- [ ] Todos los componentes funcionan

---

## 📞 Comandos Rápidos

### Reiniciar todo desde cero

```cmd
# Terminal 1 - Backend
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm start
```

### Ver logs del backend

```cmd
# Los logs aparecen en la terminal donde ejecutaste uvicorn
# Busca errores en rojo
```

### Limpiar y reinstalar frontend

```cmd
cd frontend
rmdir /s /q node_modules
del package-lock.json
npm install
npm start
```

---

**Universidad del Quindío**  
**Análisis de Algoritmos - 2026**  
**Proyecto: Análisis Algorítmico de Activos Financieros BVC**
