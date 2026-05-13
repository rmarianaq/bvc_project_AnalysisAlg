# BVC Project — AnalysisAlg

Proyecto universitario de análisis algorítmico sobre datos financieros reales de la
Bolsa de Valores de Colombia (BVC) y activos globales.

**Universidad del Quindío — Ingeniería de Sistemas y Computación**
**Materia: Análisis de Algoritmos**

---

## Requisitos previos

Instalar las siguientes herramientas antes de continuar:

| Herramienta | Versión mínima | Descarga |
|---|---|---|
| Python | 3.11 | https://www.python.org/downloads/ |
| PostgreSQL | 16 | https://www.enterprisedb.com/downloads/postgres-postgresql-downloads |
| Node.js | LTS | https://nodejs.org/en |
| Git | cualquiera | https://git-scm.com/downloads |

> **Windows:** al instalar PostgreSQL, agregar `C:\Program Files\PostgreSQL\16\bin` al PATH del sistema.

---

## Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/bvc_project_AnalysisAlg.git
cd bvc_project_AnalysisAlg
```

### 2. Crear la base de datos
```bash
psql -U postgres -c "CREATE DATABASE bvc_analysis;"
```

### 3. Configurar las variables de entorno

Crear el archivo `backend/.env` con el siguiente contenido:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bvc_analysis
DB_USER=postgres
DB_PASSWORD=tu_contraseña_de_postgres
```

> El archivo `.env` está en `.gitignore` y nunca se sube al repositorio.

### 4. Crear el entorno virtual e instalar dependencias
```bash
cd backend
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**Mac / Linux:**
```bash
source venv/bin/activate
```
```bash
pip install -r requirements.txt
```

O instalar manualmente:
```bash
pip install fastapi uvicorn psycopg2-binary python-dotenv requests matplotlib seaborn reportlab numpy
```

---

## Ejecución del proyecto

Todos los comandos se ejecutan desde la carpeta `backend/` con el entorno virtual activo.

### Paso 1 — Crear las tablas en la base de datos
```bash
python -c "from app.core.models import create_tables; create_tables()"
```

### Paso 2 — Ejecutar el ETL (descarga de datos)
```bash
python -c "from app.etl.extractor import run_etl; run_etl()"
```

> Este paso descarga datos históricos de 22 activos desde Yahoo Finance.
> Tarda aproximadamente 30 segundos dependiendo de la conexión.

### Paso 3 — Limpiar los datos
```bash
python -c "from app.etl.cleaner import run_cleaning; run_cleaning()"
```

### Paso 4 — Unificar el dataset
```bash
python -c "from app.etl.loader import run_loader; run_loader()"
```

### Paso 5 — Crear tablas de caché
```bash
psql -U postgres -d bvc_analysis -f create_cache_tables.sql
```

> Este paso crea las tablas necesarias para el sistema de caché que mejora
> el rendimiento 100x (de segundos a milisegundos).

### Paso 6 — Pre-calcular datos (Sistema de Caché)
```bash
python -m app.cache.precompute
```

> Este paso pre-calcula y guarda:
> - Matriz de correlación (253 correlaciones)
> - Volatilidad de todos los activos (22 activos)
> - Benchmark de ordenamiento (12 algoritmos)
> 
> Tarda aproximadamente 1-2 minutos y mejora el rendimiento 100x.

### Paso 7 — Ejecutar el benchmark de algoritmos (Opcional)
```bash
python -c "from app.sorting.benchmark import run_benchmark, generate_chart; generate_chart(run_benchmark())"
```

> Este paso ejecuta los 12 algoritmos de ordenamiento y genera la imagen
> `benchmark_chart.png` en la carpeta `backend/`.
> Selection Sort puede tardar varios minutos sobre el dataset completo.
> **Nota:** Los resultados ya están en caché, este paso es opcional.

### Paso 8 — Análisis de patrones y volatilidad (Opcional)
```bash
python -c "from app.similarity.patterns import get_all_assets_volatility; [print(f\"{a['ticker']}: {a['annual_volatility']:.2f}% - {a['risk_level']}\") for a in get_all_assets_volatility()]"
```

> Este paso calcula la volatilidad de todos los activos y los clasifica
> en: CONSERVADOR, MODERADO o AGRESIVO.
> **Nota:** Los resultados ya están en caché, este paso es opcional.

---

## Iniciar el servidor FastAPI (Requerimiento 4 y 5)
```bash
uvicorn app.main:app --reload
```

La API queda disponible en `http://localhost:8000`.
La documentación automática está en `http://localhost:8000/docs`.

---

## Iniciar el Frontend (Requerimiento 5)

### Primera vez - Instalar dependencias:
```bash
cd frontend
npm install
```

### Iniciar aplicación React:
```bash
npm start
```

El frontend se abrirá automáticamente en `http://localhost:3000`.

**Nota:** El backend debe estar corriendo en `http://localhost:8000` para que el frontend funcione correctamente.

---

## Uso Completo del Sistema

### 1. Iniciar Backend (Terminal 1):
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

### 2. Iniciar Frontend (Terminal 2):
```bash
cd frontend
npm start
```

### 3. Acceder a la aplicación:
- **Frontend:** http://localhost:3000
- **API Backend:** http://localhost:8000
- **Documentación API:** http://localhost:8000/docs

---

### Endpoints disponibles:

| Endpoint | Método | Descripción | Rendimiento |
|---|---|---|---|
| `/assets` | GET | Lista todos los activos del portafolio | Rápido |
| `/assets/{ticker}/prices` | GET | Precios históricos de un activo | Rápido |
| `/similarity/compare` | POST | Compara dos activos (4 algoritmos) | Rápido |
| `/similarity/correlation-matrix` | GET | Matriz de correlación completa | **< 100ms** ⚡ |
| `/patterns/{ticker}` | GET | Análisis de patrones de un activo | Rápido |
| `/volatility/all` | GET | Clasificación de riesgo de todos | **< 50ms** ⚡ |
| `/volatility/{ticker}` | GET | Volatilidad de un activo | Rápido |
| `/candlestick/{ticker}` | GET | Datos para gráfico de velas + SMAs | Rápido |
| `/reports/generate-pdf` | POST | Genera reporte técnico en PDF | 2-3 min |
| `/sorting/benchmark` | GET | Resultados del benchmark | **< 50ms** ⚡ |

**⚡ = Endpoints optimizados con sistema de caché**

### Ejemplo de uso de la API:

```bash
# Obtener todos los activos
curl http://localhost:8000/assets

# Comparar dos activos
curl -X POST http://localhost:8000/similarity/compare \
  -H "Content-Type: application/json" \
  -d "{\"ticker_a\":\"VOO\",\"ticker_b\":\"SPY\"}"

# Obtener clasificación de riesgo
curl http://localhost:8000/volatility/all

# Generar reporte PDF
curl -X POST http://localhost:8000/reports/generate-pdf --output reporte.pdf
```

---

## Estructura del proyecto
```
bvc_project_AnalysisAlg/
│
├── backend/
│   ├── .env                  ← Variables de entorno (no se sube al repo)
│   ├── create_cache_tables.sql ← Script SQL para crear tablas de caché
│   ├── app/
│   │   ├── api/              ← Endpoints REST y generación de reportes
│   │   ├── cache/            ← Sistema de caché (precompute.py)
│   │   ├── core/             ← Conexión a BD y modelos
│   │   ├── etl/              ← Extracción, limpieza y carga
│   │   ├── similarity/       ← Algoritmos de similitud y patrones
│   │   ├── sorting/          ← 12 algoritmos + benchmark
│   │   └── main.py           ← API FastAPI
│   └── venv/                 ← Entorno virtual (no se sube al repo)
│
├── frontend/                 ← Aplicación React
│   ├── src/
│   │   ├── components/       ← Componentes de UI
│   │   │   ├── Dashboard/
│   │   │   ├── SimilarityAnalysis/
│   │   │   ├── VolatilityAnalysis/
│   │   │   ├── PatternAnalysis/
│   │   │   ├── CorrelationMatrix/
│   │   │   ├── CandlestickChart/
│   │   │   └── SortingBenchmark/
│   │   └── App.js
│   └── node_modules/         ← Dependencias (no se sube al repo)
│
├── .gitignore
├── README.md
├── GUIA_EJECUCION.md         ← Guía completa de ejecución desde cero
├── configuracion_inicial.bat ← Script de configuración automatizada
└── ESTRATEGIA_DESPLIEGUE.md  ← Guía de despliegue en producción
```

---

## Portafolio de activos

| Ticker | Nombre | Mercado | Tipo |
|---|---|---|---|
| ECOPETROL.CL | Ecopetrol S.A. | BVC | STOCK |
| ISA.CL | Interconexión Eléctrica | BVC | STOCK |
| GEB.CL | Grupo Energía Bogotá | BVC | STOCK |
| CIB | Bancolombia Pref. ADR | BVC | STOCK |
| NUTRESA.CL | Grupo Nutresa | BVC | STOCK |
| GRUPOSURA.CL | Grupo Sura | BVC | STOCK |
| CELSIA.CL | Celsia S.A. | BVC | STOCK |
| BOGOTA.CL | Banco de Bogotá | BVC | STOCK |
| EXITO.CL | Grupo Éxito | BVC | STOCK |
| CEMARGOS.CL | Cementos Argos | BVC | STOCK |
| VOO | Vanguard S&P 500 ETF | GLOBAL | ETF |
| QQQ | Invesco Nasdaq 100 | GLOBAL | ETF |
| GLD | SPDR Gold Trust | GLOBAL | ETF |
| TLT | iShares 20Y Treasury | GLOBAL | ETF |
| VWO | Vanguard Emerging Markets | GLOBAL | ETF |
| XLF | Financial Select Sector | GLOBAL | ETF |
| XLE | Energy Select Sector | GLOBAL | ETF |
| ARKK | ARK Innovation ETF | GLOBAL | ETF |
| BTC-USD | Bitcoin USD | GLOBAL | ETF |
| SPY | S&P 500 SPDR | GLOBAL | ETF |
| EEM | iShares MSCI Emerging | GLOBAL | ETF |
| CSPX.L | iShares Core S&P 500 | GLOBAL | ETF |

---

## Documentación del Proyecto

Este proyecto incluye documentación exhaustiva que cumple con todos los requisitos académicos:

| Documento | Descripción |
|-----------|-------------|
| **README.md** | Guía de instalación y uso (este archivo) |
| **GUIA_EJECUCION.md** | Guía completa de ejecución desde cero con sistema de caché |
| **DOCUMENTO_DISEÑO.md** | Arquitectura del sistema y decisiones de diseño |
| **DETALLES_IMPLEMENTACION.md** | Explicación técnica detallada de cada requerimiento |
| **USO_INTELIGENCIA_ARTIFICIAL.md** | Declaración transparente del uso de IA |
| **CUMPLIMIENTO_RESTRICCIONES.md** | Verificación de cumplimiento de todas las restricciones |
| **ESTADO_PROYECTO.md** | Estado de completitud de requerimientos |
| **EJEMPLOS_USO.md** | Ejemplos prácticos de uso de la API |
| **ESTRATEGIA_DESPLIEGUE.md** | Guía de despliegue gratuito en producción |
| **backend/GUIA_CACHE.md** | Documentación detallada del sistema de caché |
| **EXPLICACION_SIMILITUD_MONEDAS.md** | Explicación técnica de similitud entre diferentes monedas |

### Sistema de Caché - Optimización de Rendimiento

El proyecto implementa un sistema de caché que pre-calcula datos que no cambian:

**Mejora de Rendimiento:**
```
Antes (Sin Caché):
  Matriz de correlación:  5-10 segundos  🐌
  Volatilidad:            2-3 segundos   🐌
  Benchmark:              10-15 segundos 🐌

Después (Con Caché):
  Matriz de correlación:  < 100ms  ⚡
  Volatilidad:            < 50ms   ⚡
  Benchmark:              < 50ms   ⚡

Mejora: 100x más rápido!
```

**Ventajas:**
- ✅ Respuestas instantáneas en el frontend
- ✅ Menor carga en el servidor
- ✅ Permite despliegue en planes gratuitos
- ✅ Mejor experiencia de usuario

**Documentación completa:** Ver `backend/GUIA_CACHE.md`

### Cumplimiento de Restricciones Académicas

✅ **Documento de diseño con arquitectura:** `DOCUMENTO_DISEÑO.md`  
✅ **Explicación técnica por requerimiento:** `DETALLES_IMPLEMENTACION.md`  
✅ **Documentación de uso de IA:** `USO_INTELIGENCIA_ARTIFICIAL.md`  
✅ **No uso de yfinance/pandas_datareader:** Peticiones HTTP directas  
✅ **No uso de funciones de alto nivel:** Implementación manual de algoritmos  
✅ **No datasets estáticos:** ETL automatizado reproducible  
✅ **Scraping ético:** Rate limiting, timeout, User-Agent  
✅ **Análisis de complejidad:** Documentado para cada algoritmo  

**Verificación completa:** Ver `CUMPLIMIENTO_RESTRICCIONES.md`

## Uso de inteligencia artificial

Este proyecto utilizó **Claude 3.5 Sonnet (Anthropic)** como herramienta de apoyo.

**Áreas donde SE usó IA:**
- Código boilerplate (estructura de archivos, configuración)
- Documentación técnica (redacción de README, docstrings)
- Debugging (identificación de errores)

**Áreas donde NO SE usó IA (100% trabajo original):**
- Diseño algorítmico
- Análisis de complejidad
- Implementación de algoritmos core
- Decisiones arquitectónicas
- Validación de resultados

**Declaración completa:** Ver `USO_INTELIGENCIA_ARTIFICIAL.md`

El diseño algorítmico, el análisis de complejidad y los resultados son responsabilidad
del equipo de desarrollo, conforme a los lineamientos del enunciado del proyecto.

---

## Notas importantes

- No modificar el archivo `venv/` ni subirlo al repositorio.
- El archivo `.env` contiene credenciales sensibles y está excluido del repositorio.
- La imagen `benchmark_chart.png` se genera automáticamente y está excluida del repositorio.
- Para reproducir los resultados desde cero, ejecutar los pasos 1 al 8 en orden.
- **Sistema de caché:** Ejecutar `python -m app.cache.precompute` después de actualizar datos.
- **Despliegue:** Ver `ESTRATEGIA_DESPLIEGUE.md` para instrucciones de despliegue gratuito.

---

## Guías Rápidas

### Configuración Inicial Automatizada
```bash
# Ejecutar el script de configuración (Windows)
configuracion_inicial.bat
```

### Configuración Manual Completa
Ver `GUIA_EJECUCION.md` para instrucciones paso a paso desde cero.

### Re-calcular Caché
```bash
cd backend
venv\Scripts\activate
python -m app.cache.precompute
```

### Verificar Caché
```bash
cd backend
venv\Scripts\activate
python -m app.cache.precompute verify
```
