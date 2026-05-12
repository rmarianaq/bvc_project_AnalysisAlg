# Detalles de Implementación por Requerimiento

**Proyecto:** Análisis Algorítmico BVC  
**Universidad del Quindío**  
**Fecha:** Mayo 12, 2026

---

## REQUERIMIENTO 1: ETL - Extracción, Limpieza y Unificación

### 1.1 Descripción Técnica

El proceso ETL automatiza la descarga, limpieza y unificación de datos financieros históricos de 22 activos (10 BVC + 12 globales) con un horizonte de 5+ años.

### 1.2 Implementación del Extractor

**Archivo:** `backend/app/etl/extractor.py`

#### 1.2.1 Construcción Manual de URLs

```python
def build_url(ticker: str) -> str:
    """
    Construye la URL de la API de Yahoo Finance manualmente.
    
    NO SE USA: yfinance, pandas_datareader
    SE USA: Construcción manual de strings
    
    Parámetros de la API:
    - interval=1d: datos diarios
    - range=5y: últimos 5 años
    """
    base = "https://query1.finance.yahoo.com/v8/finance/chart/"
    return f"{base}{ticker}?interval=1d&range=5y"
```

**Justificación técnica:**
- API pública de Yahoo Finance
- Sin autenticación requerida
- Formato JSON estándar
- Datos históricos confiables

#### 1.2.2 Petición HTTP Directa

```python
def fetch_ticker_data(ticker: str) -> dict:
    """
    Petición HTTP directa sin librerías de alto nivel.
    
    Manejo de errores:
    1. Timeout (15 segundos)
    2. ConnectionError (sin internet)
    3. HTTP errors (404, 500, etc.)
    4. JSON inválido
    """
    url = build_url(ticker)
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        
        if response.status_code != 200:
            return {"success": False, "error": f"HTTP {response.status_code}"}
        
        data = response.json()
        result = data.get("chart", {}).get("result")
        
        if not result:
            return {"success": False, "error": "Respuesta vacía"}
        
        return {"success": True, "data": result[0]}
    
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Timeout"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Sin conexión"}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

**Complejidad:** O(1) por petición, O(n) para n activos

#### 1.2.3 Parsing Manual de JSON

```python
def parse_prices(raw_data: dict) -> list:
    """
    Parsing manual del JSON de Yahoo Finance.
    
    NO SE USA: pandas.read_json(), yfinance
    SE USA: Navegación manual del diccionario
    
    Estructura del JSON:
    {
        "timestamp": [unix_time1, unix_time2, ...],
        "indicators": {
            "quote": [{
                "open": [price1, price2, ...],
                "high": [...],
                "low": [...],
                "close": [...],
                "volume": [...]
            }]
        }
    }
    """
    timestamps = raw_data.get("timestamp", [])
    indicators = raw_data.get("indicators", {})
    quotes = indicators.get("quote", [{}])[0]
    
    opens = quotes.get("open", [])
    highs = quotes.get("high", [])
    lows = quotes.get("low", [])
    closes = quotes.get("close", [])
    volumes = quotes.get("volume", [])
    
    prices = []
    for i in range(len(timestamps)):
        # Filtrar valores None
        if None in (opens[i], highs[i], lows[i], closes[i], volumes[i]):
            continue
        
        # Convertir timestamp UNIX a fecha
        date = datetime.utcfromtimestamp(timestamps[i]).strftime("%Y-%m-%d")
        
        prices.append({
            "date": date,
            "open": round(float(opens[i]), 6),
            "high": round(float(highs[i]), 6),
            "low": round(float(lows[i]), 6),
            "close": round(float(closes[i]), 6),
            "volume": int(volumes[i])
        })
    
    return prices
```

**Complejidad:** O(n) donde n = número de registros

**Decisiones de diseño:**
1. **Redondeo a 6 decimales:** Precisión suficiente para precios
2. **Filtrado de None:** Evita datos corruptos
3. **Conversión de tipos:** Garantiza consistencia

### 1.3 Implementación del Cleaner

**Archivo:** `backend/app/etl/cleaner.py`

#### 1.3.1 Detección de Anomalías

```python
def detect_anomalies(prices: list) -> dict:
    """
    Detecta 4 tipos de anomalías:
    1. Valores nulos
    2. Precios negativos o cero
    3. Volumen cero
    4. Fechas duplicadas
    
    Complejidad: O(n)
    """
    nulls = []
    negatives = []
    zero_volume = []
    duplicates = []
    seen_dates = {}
    
    for i, price in enumerate(prices):
        date = str(price["date"])
        
        # Detectar duplicados con hash table
        if date in seen_dates:
            duplicates.append(i)
        else:
            seen_dates[date] = i
        
        # Detectar nulos
        for field in ["open", "high", "low", "close", "volume"]:
            if price[field] is None:
                nulls.append({"index": i, "date": date, "field": field})
        
        # Detectar negativos
        for field in ["open", "high", "low", "close"]:
            if price[field] is not None and price[field] <= 0:
                negatives.append({"index": i, "date": date, "field": field})
        
        # Detectar volumen cero
        if price["volume"] is not None and price["volume"] == 0:
            zero_volume.append({"index": i, "date": date})
    
    return {
        "nulls": nulls,
        "negatives": negatives,
        "zero_volume": zero_volume,
        "duplicates": duplicates
    }
```

**Complejidad:** O(n) con hash table para duplicados

#### 1.3.2 Interpolación Lineal

```python
def interpolate_linear(prices: list, index: int, field: str) -> float:
    """
    Interpolación lineal para valores faltantes.
    
    Restricción: Solo interpola si gap ≤ 2 días
    
    Fórmula:
        v = v_ant + (v_sig - v_ant) × (pos / total_gap)
    
    Complejidad: O(w) donde w = tamaño del gap
    """
    # Buscar valor anterior no nulo
    prev_val = None
    prev_dist = 0
    for i in range(index - 1, -1, -1):
        if prices[i][field] is not None and prices[i][field] > 0:
            prev_val = prices[i][field]
            prev_dist = index - i
            break
    
    # Buscar valor siguiente no nulo
    next_val = None
    next_dist = 0
    for i in range(index + 1, len(prices)):
        if prices[i][field] is not None and prices[i][field] > 0:
            next_val = prices[i][field]
            next_dist = i - index
            break
    
    # Validar gap
    if prev_dist > 2 or next_dist > 2:
        return None  # Gap muy grande, eliminar
    
    if prev_val is None or next_val is None:
        return None  # No hay valores para interpolar
    
    # Aplicar interpolación lineal
    total_gap = prev_dist + next_dist
    interpolated = prev_val + (next_val - prev_val) * (prev_dist / total_gap)
    return round(interpolated, 6)
```

**Justificación del umbral (gap ≤ 2):**
- **Gap pequeño:** Interpolación confiable
- **Gap grande:** Mejor eliminar que introducir sesgo
- **Impacto algorítmico:** Preserva integridad de series temporales

**Complejidad:** O(w) donde w = tamaño del gap

### 1.4 Implementación del Loader

**Archivo:** `backend/app/etl/loader.py`

#### 1.4.1 Forward Fill

```python
def forward_fill_unified() -> int:
    """
    Propaga el último precio conocido hacia adelante.
    
    Estrategia: Forward fill (no interpolación)
    Justificación: Conservador, no inventa datos
    
    Impacto algorítmico:
    - Alinea calendarios BVC vs NYSE
    - Elimina sesgo en algoritmos de similitud
    - Series de igual longitud para comparación
    
    Complejidad: O(n × m) donde n = fechas, m = activos
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, ticker FROM assets ORDER BY ticker;")
    assets = cursor.fetchall()
    
    cursor.execute("SELECT DISTINCT trade_date FROM daily_prices ORDER BY trade_date;")
    all_dates = [row[0] for row in cursor.fetchall()]
    
    filled = 0
    
    for asset_id, ticker in assets:
        cursor.execute("""
            SELECT trade_date, close_price FROM daily_prices
            WHERE asset_id = %s ORDER BY trade_date;
        """, (asset_id,))
        rows = {row[0]: row[1] for row in cursor.fetchall()}
        
        last_price = None
        for date in all_dates:
            if date in rows:
                last_price = rows[date]
            elif last_price is not None:
                # Fecha sin registro → insertar con forward fill
                cursor.execute("""
                    INSERT INTO daily_prices
                        (asset_id, trade_date, close_price)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (asset_id, trade_date) DO NOTHING;
                """, (asset_id, date, last_price))
                filled += cursor.rowcount
    
    conn.commit()
    cursor.close()
    conn.close()
    return filled
```

**Complejidad:** O(n × m)

**Alternativas consideradas:**
1. **Interpolación:** Rechazada, inventa datos
2. **Eliminar fechas:** Rechazada, pierde información
3. **Forward fill:** ✅ Seleccionada, conservadora

---

## REQUERIMIENTO 2: Algoritmos de Similitud

### 2.1 Descripción Técnica

Implementación de 4 algoritmos de similitud entre series temporales, todos desde cero sin librerías de alto nivel.

### 2.2 Distancia Euclidiana

**Archivo:** `backend/app/similarity/algorithms.py`

```python
def euclidean_distance(series_a: list, series_b: list) -> float:
    """
    Distancia euclidiana entre dos series.
    
    Fórmula: d = √(Σ(a_i - b_i)²)
    
    NO SE USA: scipy.spatial.distance.euclidean
    SE USA: Bucle manual con acumulador
    
    Complejidad temporal: O(n)
    Complejidad espacial: O(1)
    
    Interpretación:
    - d = 0: Series idénticas
    - d pequeño: Series similares
    - d grande: Series diferentes
    """
    if len(series_a) != len(series_b):
        raise ValueError("Las series deben tener la misma longitud")
    
    total = 0.0
    for i in range(len(series_a)):
        diff = series_a[i] - series_b[i]
        total += diff * diff
    
    return math.sqrt(total)
```

**Análisis de complejidad:**
- **Mejor caso:** O(n) - siempre recorre toda la serie
- **Peor caso:** O(n) - siempre recorre toda la serie
- **Promedio:** O(n)
- **Espacio:** O(1) - solo variables escalares

### 2.3 Correlación de Pearson

```python
def pearson_correlation(series_a: list, series_b: list) -> float:
    """
    Correlación de Pearson entre dos series.
    
    Fórmula: r = Σ((a_i - μ_a)(b_i - μ_b)) / (σ_a × σ_b)
    
    NO SE USA: numpy.corrcoef, scipy.stats.pearsonr
    SE USA: Implementación manual en dos pasadas
    
    Complejidad temporal: O(n)
    Complejidad espacial: O(1)
    
    Interpretación:
    - r = 1.0: Perfectamente correlacionados
    - r = 0.0: Sin correlación lineal
    - r = -1.0: Inversamente correlacionados
    """
    n = len(series_a)
    if n != len(series_b):
        raise ValueError("Las series deben tener la misma longitud")
    
    # Primera pasada: calcular medias
    mean_a = sum(series_a) / n
    mean_b = sum(series_b) / n
    
    # Segunda pasada: calcular correlación
    numerator = 0.0
    denom_a = 0.0
    denom_b = 0.0
    
    for i in range(n):
        diff_a = series_a[i] - mean_a
        diff_b = series_b[i] - mean_b
        numerator += diff_a * diff_b
        denom_a += diff_a * diff_a
        denom_b += diff_b * diff_b
    
    denominator = math.sqrt(denom_a * denom_b)
    
    if denominator == 0:
        return 0.0
    
    return numerator / denominator
```

**Análisis de complejidad:**
- **Temporal:** O(n) - dos pasadas sobre los datos
- **Espacial:** O(1) - solo acumuladores

**Diferencia con Coseno:**
- Pearson resta la media (centra los datos)
- Coseno no resta la media (orientación del vector)

### 2.4 Dynamic Time Warping (DTW)

```python
def dtw_distance(series_a: list, series_b: list) -> float:
    """
    Dynamic Time Warping - distancia con alineación temporal.
    
    Permite comparar series desfasadas en el tiempo.
    
    Fórmula recursiva:
        dtw[i][j] = |a_i - b_j| + min(
            dtw[i-1][j],      # inserción
            dtw[i][j-1],      # eliminación
            dtw[i-1][j-1]     # coincidencia
        )
    
    NO SE USA: dtaidistance, fastdtw
    SE USA: Programación dinámica manual
    
    Complejidad temporal: O(n × m)
    Complejidad espacial: O(n × m)
    """
    n = len(series_a)
    m = len(series_b)
    
    # Matriz de costos acumulados
    dtw = [[float('inf')] * (m + 1) for _ in range(n + 1)]
    dtw[0][0] = 0.0
    
    # Llenar matriz con programación dinámica
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = abs(series_a[i - 1] - series_b[j - 1])
            dtw[i][j] = cost + min(
                dtw[i - 1][j],      # inserción
                dtw[i][j - 1],      # eliminación
                dtw[i - 1][j - 1]   # coincidencia
            )
    
    return dtw[n][m]
```

**Análisis de complejidad:**
- **Temporal:** O(n × m) - matriz completa
- **Espacial:** O(n × m) - matriz de DP

**Ventaja sobre Euclidiana:**
- Euclidiana: Compara punto a punto (rígido)
- DTW: Permite desfases temporales (flexible)

**Ejemplo de uso:**
- Comparar patrones de precios con diferentes velocidades
- Detectar similitud en tendencias desfasadas

---

## REQUERIMIENTO 3: Patrones y Volatilidad

### 3.1 Ventana Deslizante - Días Consecutivos al Alza

**Archivo:** `backend/app/similarity/patterns.py`

```python
def detect_consecutive_rises(prices: list, window_size: int = 3) -> dict:
    """
    Patrón 1: Secuencias de días consecutivos al alza.
    
    Algoritmo: Sliding Window
    
    Pseudocódigo:
        para i desde 0 hasta n - w + 1:
            es_creciente = verdadero
            para j desde i hasta i + w - 2:
                si precio[j+1] ≤ precio[j]:
                    es_creciente = falso
                    romper
            si es_creciente:
                agregar ocurrencia
    
    Complejidad: O(n × w)
    - n = longitud de la serie
    - w = tamaño de la ventana
    
    Espacio: O(k) donde k = número de ocurrencias
    """
    n = len(prices)
    if n < window_size:
        return {"frequency": 0, "occurrences": [], "total_windows": 0}
    
    occurrences = []
    
    # Ventana deslizante
    for i in range(n - window_size + 1):
        is_rising = True
        
        # Verificar si todos los precios son crecientes
        for j in range(i, i + window_size - 1):
            if prices[j + 1]["price"] <= prices[j]["price"]:
                is_rising = False
                break
        
        if is_rising:
            change_pct = ((prices[i + window_size - 1]["price"] - prices[i]["price"]) 
                         / prices[i]["price"] * 100)
            
            occurrences.append({
                "start_date": prices[i]["date"],
                "end_date": prices[i + window_size - 1]["date"],
                "start_price": prices[i]["price"],
                "end_price": prices[i + window_size - 1]["price"],
                "change_pct": change_pct
            })
    
    total_windows = n - window_size + 1
    frequency = len(occurrences)
    
    return {
        "frequency": frequency,
        "occurrences": occurrences,
        "total_windows": total_windows,
        "frequency_pct": (frequency / total_windows * 100) if total_windows > 0 else 0
    }
```

**Análisis de complejidad:**
- **Mejor caso:** O(n) - todas las ventanas son crecientes (break nunca se ejecuta)
- **Peor caso:** O(n × w) - ninguna ventana es creciente
- **Promedio:** O(n × w)

### 3.2 Ventana Deslizante - Picos de Volatilidad

```python
def detect_volatility_spikes(prices: list, window_size: int = 5, threshold: float = 2.0) -> dict:
    """
    Patrón 2: Picos de volatilidad.
    
    Formalización matemática:
    - σ_ventana > threshold × σ_global
    
    Donde:
    - σ_ventana = desviación estándar de la ventana
    - σ_global = desviación estándar de toda la serie
    - threshold = multiplicador (por defecto 2.0)
    
    Complejidad: O(n × w)
    - O(n) para calcular σ_global
    - O((n-1) × w) para ventanas deslizantes
    """
    n = len(prices)
    if n < window_size + 1:
        return {"frequency": 0, "occurrences": [], "total_windows": 0}
    
    # Calcular retornos diarios - O(n)
    returns = []
    for i in range(1, n):
        if prices[i - 1]["price"] != 0:
            r = (prices[i]["price"] - prices[i - 1]["price"]) / prices[i - 1]["price"]
            returns.append(r)
    
    if len(returns) < window_size:
        return {"frequency": 0, "occurrences": [], "total_windows": 0}
    
    # Calcular volatilidad global - O(n)
    mean_return = sum(returns) / len(returns)
    variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
    global_std = math.sqrt(variance)
    
    occurrences = []
    
    # Ventana deslizante - O(n × w)
    for i in range(len(returns) - window_size + 1):
        window_returns = returns[i:i + window_size]
        
        # Calcular desviación estándar de la ventana - O(w)
        window_mean = sum(window_returns) / window_size
        window_variance = sum((r - window_mean) ** 2 for r in window_returns) / window_size
        window_std = math.sqrt(window_variance)
        
        # Detectar pico
        if window_std > threshold * global_std:
            occurrences.append({
                "start_date": prices[i + 1]["date"],
                "end_date": prices[i + window_size]["date"],
                "window_volatility": round(window_std * 100, 4),
                "global_volatility": round(global_std * 100, 4),
                "ratio": round(window_std / global_std, 2) if global_std > 0 else 0
            })
    
    total_windows = len(returns) - window_size + 1
    frequency = len(occurrences)
    
    return {
        "frequency": frequency,
        "occurrences": occurrences,
        "total_windows": total_windows,
        "frequency_pct": (frequency / total_windows * 100) if total_windows > 0 else 0,
        "global_volatility": round(global_std * 100, 4)
    }
```

**Complejidad total:** O(n) + O(n × w) = O(n × w)

### 3.3 Volatilidad Histórica

```python
def calculate_volatility(ticker: str, window: int = 252) -> dict:
    """
    Calcula volatilidad histórica anualizada.
    
    Fórmula: σ_anual = σ_diaria × √252
    
    Donde:
    - σ_diaria = desviación estándar de retornos diarios
    - 252 = días de negociación al año
    
    NO SE USA: pandas.std(), numpy.std()
    SE USA: Cálculo manual de desviación estándar
    
    Complejidad: O(n)
    """
    prices = get_price_series(ticker)
    n = len(prices)
    
    if n < 2:
        return {"ticker": ticker, "error": "Datos insuficientes"}
    
    # Calcular retornos diarios - O(n)
    returns = []
    for i in range(1, n):
        if prices[i - 1]["price"] != 0:
            r = (prices[i]["price"] - prices[i - 1]["price"]) / prices[i - 1]["price"]
            returns.append(r)
    
    if not returns:
        return {"ticker": ticker, "error": "No se pudieron calcular retornos"}
    
    # Volatilidad histórica - O(n)
    mean_return = sum(returns) / len(returns)
    variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
    daily_std = math.sqrt(variance)
    
    # Anualizar (252 días de negociación)
    annual_volatility = daily_std * math.sqrt(252)
    
    # Volatilidad móvil (últimos N días) - O(window)
    recent_window = min(window, len(returns))
    recent_returns = returns[-recent_window:]
    recent_mean = sum(recent_returns) / len(recent_returns)
    recent_variance = sum((r - recent_mean) ** 2 for r in recent_returns) / len(recent_returns)
    recent_std = math.sqrt(recent_variance)
    recent_annual = recent_std * math.sqrt(252)
    
    return {
        "ticker": ticker,
        "daily_volatility": round(daily_std * 100, 4),
        "annual_volatility": round(annual_volatility * 100, 2),
        "recent_volatility": round(recent_annual * 100, 2),
        "mean_return": round(mean_return * 100, 4),
        "data_points": len(returns)
    }
```

**Complejidad:** O(n)

### 3.4 Clasificación de Riesgo

```python
def classify_risk(annual_volatility: float) -> str:
    """
    Clasifica activos por nivel de riesgo.
    
    Criterios (estándar en finanzas):
    - Conservador: σ < 15%
    - Moderado: 15% ≤ σ < 25%
    - Agresivo: σ ≥ 25%
    
    Complejidad: O(1)
    """
    if annual_volatility < 15:
        return "CONSERVADOR"
    elif annual_volatility < 25:
        return "MODERADO"
    else:
        return "AGRESIVO"
```

**Justificación de umbrales:**
- **15%:** Volatilidad típica de bonos y ETFs conservadores
- **25%:** Volatilidad típica de acciones de mercados desarrollados
- **>25%:** Volatilidad de acciones emergentes, criptomonedas, etc.

---

## CUMPLIMIENTO DE RESTRICCIONES

### ✅ No uso de librerías prohibidas

**Verificado:**
```bash
grep -r "yfinance" backend/app/     # Sin resultados
grep -r "pandas_datareader" backend/app/  # Sin resultados
grep -r "scipy" backend/app/        # Sin resultados
grep -r "sklearn" backend/app/      # Sin resultados
```

### ✅ Implementación manual de algoritmos

Todos los algoritmos implementados con:
- Bucles for/while
- Estructuras básicas (listas, diccionarios)
- Operaciones matemáticas básicas
- Sin funciones de alto nivel

### ✅ Peticiones HTTP directas

- Construcción manual de URLs
- Parsing explícito de JSON
- Manejo manual de errores

### ✅ Análisis de complejidad

Cada algoritmo tiene:
- Análisis de complejidad temporal
- Análisis de complejidad espacial
- Casos mejor/peor/promedio
- Justificación de decisiones

---

**Versión:** 1.0.0  
**Última actualización:** Mayo 12, 2026
