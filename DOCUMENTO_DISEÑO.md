# Documento de Diseño y Arquitectura
## Proyecto: Análisis Algorítmico BVC

**Universidad del Quindío - Ingeniería de Sistemas y Computación**  
**Materia:** Análisis de Algoritmos  
**Fecha:** Mayo 12, 2026

---

## 1. INTRODUCCIÓN

### 1.1 Propósito del Documento
Este documento describe el diseño arquitectónico y las decisiones técnicas del proyecto de análisis algorítmico de activos financieros de la Bolsa de Valores de Colombia (BVC) y activos globales.

### 1.2 Alcance
El sistema implementa algoritmos clásicos para:
- Extracción, transformación y carga (ETL) de datos financieros
- Análisis de similitud entre series temporales
- Detección de patrones mediante ventanas deslizantes
- Clasificación de riesgo por volatilidad
- Visualización y generación de reportes

### 1.3 Audiencia
- Estudiantes del curso de Análisis de Algoritmos
- Evaluadores del proyecto
- Desarrolladores que deseen extender el sistema

---

## 2. ARQUITECTURA DEL SISTEMA

### 2.1 Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  API REST (FastAPI)                                   │   │
│  │  - Endpoints HTTP                                     │   │
│  │  - Documentación Swagger                              │   │
│  │  - Validación con Pydantic                            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE LÓGICA DE NEGOCIO                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Similarity   │  │  Patterns    │  │   Sorting    │      │
│  │ - Euclidean  │  │ - Sliding    │  │ - 12 algos   │      │
│  │ - Pearson    │  │   Window     │  │ - Benchmark  │      │
│  │ - Cosine     │  │ - Volatility │  │              │      │
│  │ - DTW        │  │ - Risk Class │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  ETL Pipeline                                         │   │
│  │  - Extractor → Cleaner → Loader                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Reports Generator                                    │   │
│  │  - Heatmaps, Charts, PDF                             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE DATOS                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  PostgreSQL Database                                  │   │
│  │  - assets                                             │   │
│  │  - daily_prices                                       │   │
│  │  - etl_log                                            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    FUENTES EXTERNAS                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Yahoo Finance API (query1.finance.yahoo.com)        │   │
│  │  - Peticiones HTTP directas                          │   │
│  │  - Parsing manual de JSON                            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Patrón Arquitectónico
**Arquitectura en Capas (Layered Architecture)**

**Justificación:**
- Separación clara de responsabilidades
- Facilita el testing y mantenimiento
- Permite evolución independiente de cada capa
- Cumple con principios SOLID

### 2.3 Tecnologías Utilizadas

| Componente | Tecnología | Justificación |
|------------|------------|---------------|
| Lenguaje | Python 3.11+ | Ecosistema científico, legibilidad |
| Base de datos | PostgreSQL 16 | ACID, integridad referencial |
| API Framework | FastAPI | Alto rendimiento, validación automática |
| HTTP Client | requests | Estándar de facto, simple y robusto |
| Visualización | matplotlib, seaborn | Control fino sobre gráficos |
| PDF | ReportLab | Generación programática de PDFs |

---

## 3. DISEÑO DE MÓDULOS

### 3.1 Módulo ETL (app/etl/)

#### 3.1.1 Extractor (extractor.py)

**Responsabilidad:** Descarga de datos desde Yahoo Finance API

**Diseño:**
```python
build_url(ticker) → str
    ↓
fetch_ticker_data(ticker) → dict
    ↓
parse_prices(raw_data) → list[dict]
    ↓
save_asset() + save_prices()
```

**Decisiones de diseño:**
1. **Peticiones HTTP directas:** Se usa `requests.get()` con construcción manual de URLs
2. **Parsing manual:** Se navega la estructura JSON sin librerías de alto nivel
3. **Manejo de errores:** Try-except explícito para timeout, conexión, HTTP errors
4. **Rate limiting:** Sleep de 1 segundo entre peticiones (ético)

**Cumplimiento de restricciones:**
- ✅ NO usa yfinance, pandas_datareader
- ✅ Construcción manual de URLs
- ✅ Parsing explícito del JSON
- ✅ Manejo manual de timestamps UNIX

#### 3.1.2 Cleaner (cleaner.py)

**Responsabilidad:** Detección y corrección de anomalías

**Algoritmos implementados:**

1. **Detección de anomalías - O(n)**
```
Para cada registro:
    - Verificar duplicados (hash de fechas)
    - Detectar valores nulos
    - Detectar precios negativos/cero
    - Detectar volumen cero
```

2. **Interpolación lineal - O(n × w)**
```
Para cada valor faltante:
    - Buscar valor anterior no nulo (O(w))
    - Buscar valor siguiente no nulo (O(w))
    - Si gap ≤ 2: interpolar
    - Si gap > 2: eliminar registro
    
Fórmula: v = v_ant + (v_sig - v_ant) × (pos / total_gap)
```

**Justificación del umbral (gap ≤ 2):**
- Gaps pequeños: interpolación confiable
- Gaps grandes: mejor eliminar que introducir sesgo

#### 3.1.3 Loader (loader.py)

**Responsabilidad:** Unificación del dataset

**Algoritmo de unificación - O(n × m)**
```
1. Obtener todas las fechas únicas (O(n))
2. Para cada activo (m activos):
    - LEFT JOIN con fechas (O(n))
    - Crear columna con precios de cierre
3. Generar vista SQL dinámica
```

**Forward Fill - O(n × m)**
```
Para cada activo:
    Para cada fecha en calendario completo:
        Si fecha sin precio:
            Usar último precio conocido
        Sino:
            Actualizar último precio conocido
```

**Justificación:**
- Alinea calendarios BVC vs NYSE
- Elimina sesgo en algoritmos de similitud
- Permite comparaciones justas entre activos

### 3.2 Módulo Similarity (app/similarity/)

#### 3.2.1 Algoritmos (algorithms.py)

**1. Distancia Euclidiana**
```
Fórmula: d = √(Σ(a_i - b_i)²)
Complejidad: O(n)
Espacio: O(1)

Pseudocódigo:
    suma = 0
    para i desde 0 hasta n-1:
        suma += (a[i] - b[i])²
    retornar √suma
```

**2. Correlación de Pearson**
```
Fórmula: r = Σ((a_i - μ_a)(b_i - μ_b)) / (σ_a × σ_b)
Complejidad: O(n)
Espacio: O(1)

Pseudocódigo:
    μ_a = media(a)
    μ_b = media(b)
    numerador = Σ((a[i] - μ_a)(b[i] - μ_b))
    denominador = √(Σ(a[i] - μ_a)²) × √(Σ(b[i] - μ_b)²)
    retornar numerador / denominador
```

**3. Similitud por Coseno**
```
Fórmula: cos(θ) = (A · B) / (||A|| × ||B||)
Complejidad: O(n)
Espacio: O(1)

Pseudocódigo:
    producto_punto = Σ(a[i] × b[i])
    norma_a = √(Σ(a[i]²))
    norma_b = √(Σ(b[i]²))
    retornar producto_punto / (norma_a × norma_b)
```

**4. Dynamic Time Warping (DTW)**
```
Complejidad: O(n × m)
Espacio: O(n × m)

Pseudocódigo:
    dtw[n+1][m+1] inicializado con ∞
    dtw[0][0] = 0
    
    para i desde 1 hasta n:
        para j desde 1 hasta m:
            costo = |a[i-1] - b[j-1]|
            dtw[i][j] = costo + min(
                dtw[i-1][j],      # inserción
                dtw[i][j-1],      # eliminación
                dtw[i-1][j-1]     # coincidencia
            )
    
    retornar dtw[n][m]
```

**Cumplimiento de restricciones:**
- ✅ Implementación manual desde cero
- ✅ NO usa scipy.spatial.distance
- ✅ NO usa numpy.corrcoef
- ✅ Estructuras básicas (listas, bucles)

#### 3.2.2 Patterns (patterns.py)

**1. Ventana Deslizante - Días Consecutivos al Alza**
```
Complejidad: O(n × w)
Espacio: O(k) donde k = número de ocurrencias

Pseudocódigo:
    ocurrencias = []
    para i desde 0 hasta n - w + 1:
        es_creciente = verdadero
        para j desde i hasta i + w - 2:
            si precios[j+1] ≤ precios[j]:
                es_creciente = falso
                romper
        si es_creciente:
            agregar ocurrencia
    retornar ocurrencias
```

**2. Ventana Deslizante - Picos de Volatilidad**
```
Complejidad: O(n × w)
Espacio: O(n) para retornos

Pseudocódigo:
    retornos = calcular_retornos(precios)  # O(n)
    σ_global = desviacion_estandar(retornos)  # O(n)
    
    para i desde 0 hasta len(retornos) - w + 1:
        ventana = retornos[i:i+w]
        σ_ventana = desviacion_estandar(ventana)  # O(w)
        
        si σ_ventana > threshold × σ_global:
            agregar pico
    
    retornar picos
```

**3. Volatilidad Histórica**
```
Complejidad: O(n)
Espacio: O(n) para retornos

Fórmula: σ_anual = σ_diaria × √252

Pseudocódigo:
    retornos = []
    para i desde 1 hasta n-1:
        r = (precio[i] - precio[i-1]) / precio[i-1]
        retornos.append(r)
    
    μ = media(retornos)
    varianza = Σ((r - μ)²) / n
    σ_diaria = √varianza
    σ_anual = σ_diaria × √252
    
    retornar σ_anual
```

**Clasificación de Riesgo:**
```
si σ_anual < 15%:
    clasificación = "CONSERVADOR"
sino si σ_anual < 25%:
    clasificación = "MODERADO"
sino:
    clasificación = "AGRESIVO"
```

**Cumplimiento de restricciones:**
- ✅ Implementación manual de ventanas deslizantes
- ✅ NO usa pandas.rolling()
- ✅ Cálculo explícito de desviación estándar
- ✅ NO usa numpy.std()

### 3.3 Módulo Sorting (app/sorting/)

**12 Algoritmos de Ordenamiento Implementados**

Todos implementados manualmente sin usar `sorted()` o `list.sort()`.

**Ejemplo: QuickSort Iterativo**
```
Complejidad: O(n log n) promedio, O(n²) peor caso
Espacio: O(log n) para la pila

Pseudocódigo:
    pila = [(0, n-1)]
    
    mientras pila no vacía:
        (bajo, alto) = pila.pop()
        
        si bajo < alto:
            pivote = particion(arr, bajo, alto)
            pila.push((bajo, pivote-1))
            pila.push((pivote+1, alto))

particion(arr, bajo, alto):
    # Mediana de tres para evitar O(n²)
    medio = (bajo + alto) / 2
    ordenar(arr[bajo], arr[medio], arr[alto])
    pivote = arr[medio]
    
    i = bajo - 1
    para j desde bajo hasta alto-1:
        si arr[j] ≤ pivote:
            i++
            intercambiar(arr[i], arr[j])
    
    intercambiar(arr[i+1], arr[alto])
    retornar i + 1
```

**Cumplimiento de restricciones:**
- ✅ Implementación manual de 12 algoritmos
- ✅ NO usa funciones de ordenamiento built-in
- ✅ Análisis de complejidad documentado

### 3.4 Módulo API (app/main.py)

**Diseño RESTful**

```
GET    /assets                      → Lista de activos
GET    /assets/{ticker}/prices      → Precios históricos
POST   /similarity/compare          → Comparar 2 activos
GET    /similarity/correlation-matrix → Matriz completa
GET    /patterns/{ticker}           → Análisis de patrones
GET    /volatility/all              → Clasificación de riesgo
GET    /volatility/{ticker}         → Volatilidad específica
GET    /candlestick/{ticker}        → Datos para gráfico
POST   /reports/generate-pdf        → Generar reporte
GET    /health                      → Health check
```

**Validación con Pydantic:**
```python
class SimilarityRequest(BaseModel):
    ticker_a: str
    ticker_b: str

class SimilarityResponse(BaseModel):
    ticker_a: str
    ticker_b: str
    common_dates: int
    euclidean: float
    pearson: float
    cosine: float
    dtw: float
```

---

## 4. MODELO DE DATOS

### 4.1 Esquema de Base de Datos

```sql
-- Tabla de activos
CREATE TABLE assets (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    market VARCHAR(50) NOT NULL,
    asset_type VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de precios diarios
CREATE TABLE daily_prices (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER REFERENCES assets(id) ON DELETE CASCADE,
    trade_date DATE NOT NULL,
    open_price NUMERIC(15, 6),
    high_price NUMERIC(15, 6),
    low_price NUMERIC(15, 6),
    close_price NUMERIC(15, 6),
    volume BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(asset_id, trade_date)
);

-- Índices para optimización
CREATE INDEX idx_daily_prices_asset_date 
    ON daily_prices(asset_id, trade_date);
CREATE INDEX idx_daily_prices_date 
    ON daily_prices(trade_date);

-- Tabla de log ETL
CREATE TABLE etl_log (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    records INTEGER DEFAULT 0,
    message TEXT,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2 Vista Unificada

```sql
CREATE OR REPLACE VIEW unified_prices AS
SELECT
    dates.trade_date,
    ecopetrol.close_price AS "ECOPETROL.CL",
    isa.close_price AS "ISA.CL",
    -- ... (una columna por cada activo)
FROM (
    SELECT DISTINCT trade_date
    FROM daily_prices
    ORDER BY trade_date
) AS dates
LEFT JOIN (
    SELECT trade_date, close_price
    FROM daily_prices
    WHERE asset_id = 1
) AS ecopetrol ON dates.trade_date = ecopetrol.trade_date
-- ... (un LEFT JOIN por cada activo)
ORDER BY dates.trade_date;
```

---

## 5. FLUJO DE DATOS

### 5.1 Pipeline ETL

```
┌─────────────┐
│  EXTRACTOR  │
└──────┬──────┘
       │ 1. Construir URL manualmente
       │ 2. Petición HTTP con requests
       │ 3. Parsear JSON manualmente
       │ 4. Convertir timestamps UNIX
       │ 5. Guardar en BD
       ↓
┌─────────────┐
│   CLEANER   │
└──────┬──────┘
       │ 1. Detectar anomalías
       │ 2. Interpolar valores (gap ≤ 2)
       │ 3. Eliminar registros (gap > 2)
       │ 4. Actualizar BD
       ↓
┌─────────────┐
│   LOADER    │
└──────┬──────┘
       │ 1. Detectar gaps de calendario
       │ 2. Aplicar forward fill
       │ 3. Crear vista unificada
       │ 4. Validar integridad
       ↓
┌─────────────┐
│  DATASET    │
│  UNIFICADO  │
└─────────────┘
```

### 5.2 Flujo de Análisis

```
┌─────────────┐
│   DATASET   │
└──────┬──────┘
       │
       ├──────────────────┬──────────────────┬──────────────────┐
       ↓                  ↓                  ↓                  ↓
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ SIMILARITY  │    │  PATTERNS   │    │  SORTING    │    │   REPORTS   │
│             │    │             │    │             │    │             │
│ • Euclidean │    │ • Sliding   │    │ • 12 algos  │    │ • Heatmap   │
│ • Pearson   │    │   Window    │    │ • Benchmark │    │ • Charts    │
│ • Cosine    │    │ • Volatility│    │             │    │ • PDF       │
│ • DTW       │    │ • Risk      │    │             │    │             │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │                  │
       └──────────────────┴──────────────────┴──────────────────┘
                                  ↓
                          ┌─────────────┐
                          │  API REST   │
                          │  (FastAPI)  │
                          └─────────────┘
```

---

## 6. DECISIONES DE DISEÑO CRÍTICAS

### 6.1 ¿Por qué PostgreSQL y no SQLite?
- **Integridad referencial:** Foreign keys con CASCADE
- **Concurrencia:** Múltiples lecturas simultáneas
- **Tipos de datos:** NUMERIC para precisión financiera
- **Escalabilidad:** Preparado para millones de registros

### 6.2 ¿Por qué FastAPI y no Flask?
- **Validación automática:** Pydantic integrado
- **Documentación:** Swagger UI automático
- **Performance:** Basado en Starlette (async)
- **Type hints:** Mejor experiencia de desarrollo

### 6.3 ¿Por qué implementar DTW si es O(n²)?
- **Valor educativo:** Algoritmo de programación dinámica
- **Aplicabilidad:** Detecta similitud con desfase temporal
- **Optimización futura:** Posible implementación con FastDTW

### 6.4 ¿Por qué forward fill y no interpolación?
- **Conservador:** No inventa datos
- **Realista:** Refleja último precio conocido
- **Estándar:** Usado en finanzas (pandas.ffill())

---

## 7. ANÁLISIS DE COMPLEJIDAD

### 7.1 Complejidad Temporal

| Operación | Complejidad | Justificación |
|-----------|-------------|---------------|
| ETL Extractor | O(n) | n = registros por activo |
| ETL Cleaner | O(n × w) | w = tamaño máximo de gap |
| ETL Loader | O(n × m) | n = fechas, m = activos |
| Euclidean | O(n) | Un solo recorrido |
| Pearson | O(n) | Dos recorridos (media + correlación) |
| Cosine | O(n) | Un solo recorrido |
| DTW | O(n × m) | Matriz de programación dinámica |
| Sliding Window | O(n × w) | n = serie, w = ventana |
| Volatility | O(n) | Cálculo de desviación estándar |
| Correlation Matrix | O(m² × n) | m² pares, n = longitud serie |
| QuickSort | O(n log n) | Promedio con mediana de tres |
| HeapSort | O(n log n) | Garantizado |

### 7.2 Complejidad Espacial

| Operación | Complejidad | Justificación |
|-----------|-------------|---------------|
| Euclidean | O(1) | Variables escalares |
| Pearson | O(1) | Variables escalares |
| Cosine | O(1) | Variables escalares |
| DTW | O(n × m) | Matriz completa |
| Sliding Window | O(k) | k = ocurrencias encontradas |
| Volatility | O(n) | Array de retornos |
| QuickSort (iterativo) | O(log n) | Pila de recursión |

---

## 8. PATRONES DE DISEÑO APLICADOS

### 8.1 Strategy Pattern (Algoritmos de Similitud)
```python
# Cada algoritmo es una estrategia intercambiable
def compare_assets(ticker_a, ticker_b, strategy):
    series_a, series_b = get_aligned_returns(ticker_a, ticker_b)
    return strategy(series_a, series_b)

# Uso
result = compare_assets("VOO", "SPY", pearson_correlation)
```

### 8.2 Pipeline Pattern (ETL)
```python
# Cada etapa transforma los datos
data = extract(ticker)
data = clean(data)
data = load(data)
```

### 8.3 Repository Pattern (Acceso a Datos)
```python
# Abstracción del acceso a BD
def get_connection():
    return psycopg2.connect(...)

def get_prices_by_asset(asset_id):
    conn = get_connection()
    # ...
```

---

## 9. SEGURIDAD Y BUENAS PRÁCTICAS

### 9.1 Seguridad
- ✅ Variables de entorno para credenciales (.env)
- ✅ Validación de entrada con Pydantic
- ✅ Prepared statements (SQL injection prevention)
- ✅ Rate limiting en peticiones HTTP
- ✅ Timeout en peticiones (15 segundos)

### 9.2 Ética en Scraping
- ✅ User-Agent identificable
- ✅ Sleep entre peticiones (1 segundo)
- ✅ Manejo de errores HTTP
- ✅ Respeto a límites de la API

### 9.3 Reproducibilidad
- ✅ requirements.txt con versiones fijas
- ✅ Documentación paso a paso
- ✅ Scripts automatizados
- ✅ Seed data no requerido

---

## 10. TESTING Y VALIDACIÓN

### 10.1 Suite de Pruebas
- 9 tests automatizados (test_api.py)
- Cobertura de todos los endpoints
- Validación de respuestas
- Manejo de errores

### 10.2 Validación de Algoritmos
- Comparación VOO vs SPY (debe ser ~0.999)
- Volatilidad de BTC-USD (debe ser alta)
- Correlación de activos no relacionados (debe ser baja)

---

## 11. ESCALABILIDAD Y EXTENSIBILIDAD

### 11.1 Escalabilidad Horizontal
- API stateless (puede replicarse)
- Base de datos centralizada
- Caché potencial (Redis)

### 11.2 Extensibilidad
- Nuevos algoritmos: agregar función en algorithms.py
- Nuevos activos: agregar a ASSETS en extractor.py
- Nuevos endpoints: agregar a main.py
- Nuevos patrones: agregar a patterns.py

---

## 12. LIMITACIONES Y TRABAJO FUTURO

### 12.1 Limitaciones Actuales
- DTW es O(n²): lento para series muy largas
- Correlation matrix: tarda 1-2 minutos
- Sin caché de resultados
- Sin frontend web

### 12.2 Mejoras Futuras
- Implementar FastDTW (O(n))
- Caché con Redis
- Procesamiento paralelo (multiprocessing)
- Frontend React
- Autenticación y autorización
- Despliegue en cloud (AWS, GCP)

---

## 13. CONCLUSIONES

El sistema implementa una arquitectura en capas robusta que:
- ✅ Cumple todos los requerimientos funcionales
- ✅ Respeta todas las restricciones técnicas
- ✅ Implementa algoritmos desde cero
- ✅ Documenta complejidad algorítmica
- ✅ Es reproducible y extensible
- ✅ Sigue buenas prácticas de ingeniería

El diseño prioriza:
1. **Claridad:** Código legible y bien documentado
2. **Corrección:** Algoritmos implementados correctamente
3. **Eficiencia:** Complejidad algorítmica analizada
4. **Mantenibilidad:** Separación de responsabilidades

---

**Versión:** 1.0.0  
**Última actualización:** Mayo 12, 2026
