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
pip install fastapi uvicorn psycopg2-binary python-dotenv requests matplotlib
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

### Paso 5 — Ejecutar el benchmark de algoritmos
```bash
python -c "from app.sorting.benchmark import run_benchmark, generate_chart; generate_chart(run_benchmark())"
```

> Este paso ejecuta los 12 algoritmos de ordenamiento y genera la imagen
> `benchmark_chart.png` en la carpeta `backend/`.
> Selection Sort puede tardar varios minutos sobre el dataset completo.

---

## Iniciar el servidor FastAPI
```bash
uvicorn app.main:app --reload
```

La API queda disponible en `http://localhost:8000`.
La documentación automática está en `http://localhost:8000/docs`.

---

## Estructura del proyecto
```
bvc_project_AnalysisAlg/
│
├── backend/
│   ├── .env                  ← Variables de entorno (no se sube al repo)
│   ├── app/
│   │   ├── api/              ← Endpoints REST
│   │   ├── core/             ← Conexión a BD y modelos
│   │   ├── etl/              ← Extracción, limpieza y carga
│   │   └── sorting/          ← 12 algoritmos + benchmark
│   └── venv/                 ← Entorno virtual (no se sube al repo)
│
├── frontend/                 ← Aplicación React
│   └── src/
│
├── .gitignore
└── README.md
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

## Uso de inteligencia artificial

Este proyecto utilizó Claude (Anthropic) como herramienta de apoyo en el desarrollo.
El uso de IA se limitó a soporte en implementación y documentación.
El diseño algorítmico, el análisis de complejidad y los resultados son responsabilidad
del equipo de desarrollo, conforme a los lineamientos del enunciado del proyecto.

---

## Notas importantes

- No modificar el archivo `venv/` ni subirlo al repositorio.
- El archivo `.env` contiene credenciales sensibles y está excluido del repositorio.
- La imagen `benchmark_chart.png` se genera automáticamente y está excluida del repositorio.
- Para reproducir los resultados desde cero, ejecutar los pasos 1 al 5 en orden.
