# Ejemplos de Uso - BVC Analysis API

Este documento contiene ejemplos prácticos de cómo usar la API del proyecto.

---

## Requisitos Previos

1. Servidor corriendo:
```bash
cd backend
uvicorn app.main:app --reload
```

2. Base de datos con datos cargados (ejecutar ETL primero)

---

## 1. Verificar que la API está funcionando

### cURL:
```bash
curl http://localhost:8000/health
```

### Python:
```python
import requests

response = requests.get("http://localhost:8000/health")
print(response.json())
```

### Respuesta esperada:
```json
{
  "status": "healthy",
  "database": "connected",
  "assets_count": 22
}
```

---

## 2. Obtener lista de activos

### cURL:
```bash
curl http://localhost:8000/assets
```

### Python:
```python
import requests

response = requests.get("http://localhost:8000/assets")
assets = response.json()

print(f"Total de activos: {len(assets)}")
for asset in assets[:5]:
    print(f"{asset['ticker']}: {asset['name']}")
```

### Respuesta esperada:
```json
[
  {
    "id": 1,
    "ticker": "ECOPETROL.CL",
    "name": "Ecopetrol S.A.",
    "market": "BVC",
    "asset_type": "STOCK"
  },
  ...
]
```

---

## 3. Obtener precios históricos de un activo

### cURL:
```bash
# Últimos 10 precios de ECOPETROL
curl "http://localhost:8000/assets/ECOPETROL.CL/prices?limit=10"
```

### Python:
```python
import requests

ticker = "ECOPETROL.CL"
response = requests.get(f"http://localhost:8000/assets/{ticker}/prices?limit=10")
prices = response.json()

print(f"Últimos 10 precios de {ticker}:")
for price in prices:
    print(f"{price['date']}: ${price['close']:.2f}")
```

### Respuesta esperada:
```json
[
  {
    "date": "2024-05-10",
    "open": 2850.0,
    "high": 2900.0,
    "low": 2830.0,
    "close": 2875.0,
    "volume": 15000000
  },
  ...
]
```

---

## 4. Comparar similitud entre dos activos

### cURL:
```bash
curl -X POST http://localhost:8000/similarity/compare \
  -H "Content-Type: application/json" \
  -d '{"ticker_a":"VOO","ticker_b":"SPY"}'
```

### Python:
```python
import requests

payload = {
    "ticker_a": "VOO",
    "ticker_b": "SPY"
}

response = requests.post(
    "http://localhost:8000/similarity/compare",
    json=payload
)

result = response.json()
print(f"Comparación: {result['ticker_a']} vs {result['ticker_b']}")
print(f"Fechas comunes: {result['common_dates']}")
print(f"\nMétricas de similitud:")
print(f"  Euclidiana: {result['euclidean']:.6f}")
print(f"  Pearson:    {result['pearson']:.6f}")
print(f"  Coseno:     {result['cosine']:.6f}")
print(f"  DTW:        {result['dtw']:.6f}")
```

### Respuesta esperada:
```json
{
  "ticker_a": "VOO",
  "ticker_b": "SPY",
  "common_dates": 1258,
  "date_from": "2019-05-01",
  "date_to": "2024-05-10",
  "euclidean": 0.125678,
  "pearson": 0.999234,
  "cosine": 0.999456,
  "dtw": 15.234567
}
```

**Interpretación:**
- **Pearson cercano a 1:** Los activos están muy correlacionados (se mueven juntos)
- **Euclidiana cercana a 0:** Las series son muy similares en magnitud
- **DTW:** Distancia considerando desfases temporales

---

## 5. Obtener matriz de correlación completa

### cURL:
```bash
curl http://localhost:8000/similarity/correlation-matrix
```

### Python:
```python
import requests
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

response = requests.get("http://localhost:8000/similarity/correlation-matrix")
data = response.json()

tickers = data['tickers']
matrix = np.array(data['matrix'])

# Visualizar con heatmap
plt.figure(figsize=(12, 10))
sns.heatmap(
    matrix,
    xticklabels=tickers,
    yticklabels=tickers,
    annot=False,
    cmap='RdYlGn',
    center=0,
    vmin=-1,
    vmax=1
)
plt.title('Matriz de Correlación')
plt.tight_layout()
plt.savefig('correlation_matrix.png')
print("Matriz guardada como correlation_matrix.png")
```

**Nota:** Este endpoint puede tardar 1-2 minutos en calcular todas las correlaciones.

---

## 6. Análisis de patrones de un activo

### cURL:
```bash
curl http://localhost:8000/patterns/ECOPETROL.CL
```

### Python:
```python
import requests

ticker = "ECOPETROL.CL"
response = requests.get(f"http://localhost:8000/patterns/{ticker}")
result = response.json()

print(f"Análisis de patrones para {result['ticker']}")
print(f"\n📈 Patrón 1: Días consecutivos al alza")
print(f"  Frecuencia: {result['consecutive_rises']['frequency']} ocurrencias")
print(f"  Porcentaje: {result['consecutive_rises']['frequency_pct']:.2f}%")

print(f"\n📊 Patrón 2: Picos de volatilidad")
print(f"  Frecuencia: {result['volatility_spikes']['frequency']} ocurrencias")
print(f"  Porcentaje: {result['volatility_spikes']['frequency_pct']:.2f}%")

print(f"\n💹 Volatilidad:")
print(f"  Anual: {result['volatility_metrics']['annual_volatility']:.2f}%")
print(f"  Clasificación: {result['risk_classification']}")
```

### Respuesta esperada:
```json
{
  "ticker": "ECOPETROL.CL",
  "consecutive_rises": {
    "frequency": 145,
    "frequency_pct": 11.52,
    "total_windows": 1258,
    "top_occurrences": [...]
  },
  "volatility_spikes": {
    "frequency": 23,
    "frequency_pct": 1.83,
    "total_windows": 1257,
    "global_volatility": 2.15,
    "top_occurrences": [...]
  },
  "volatility_metrics": {
    "ticker": "ECOPETROL.CL",
    "daily_volatility": 2.15,
    "annual_volatility": 34.12,
    "recent_volatility": 28.45,
    "price_range_pct": 125.34,
    "mean_return": 0.0234,
    "data_points": 1258
  },
  "risk_classification": "AGRESIVO"
}
```

---

## 7. Clasificación de riesgo de todos los activos

### cURL:
```bash
curl http://localhost:8000/volatility/all
```

### Python:
```python
import requests
import pandas as pd

response = requests.get("http://localhost:8000/volatility/all")
results = response.json()

# Convertir a DataFrame para análisis
df = pd.DataFrame(results)

print("Clasificación de riesgo de todos los activos:")
print(df.to_string(index=False))

# Contar por categoría
print("\nDistribución por riesgo:")
print(df['risk_level'].value_counts())

# Top 5 más volátiles
print("\nTop 5 más volátiles:")
print(df.head(5)[['ticker', 'annual_volatility', 'risk_level']])
```

### Respuesta esperada:
```json
[
  {
    "ticker": "BTC-USD",
    "annual_volatility": 78.45,
    "recent_volatility": 82.12,
    "risk_level": "AGRESIVO",
    "mean_return": 0.1234
  },
  {
    "ticker": "ARKK",
    "annual_volatility": 45.23,
    "recent_volatility": 38.67,
    "risk_level": "AGRESIVO",
    "mean_return": 0.0456
  },
  ...
]
```

---

## 8. Datos para gráfico de velas (candlestick)

### cURL:
```bash
# Últimos 30 días de VOO con medias móviles
curl "http://localhost:8000/candlestick/VOO?days=30"
```

### Python con visualización:
```python
import requests
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ticker = "VOO"
response = requests.get(f"http://localhost:8000/candlestick/{ticker}?days=60")
data = response.json()

df = pd.DataFrame(data)
df['date'] = pd.to_datetime(df['date'])

# Crear gráfico de velas
fig, ax = plt.subplots(figsize=(14, 7))

for i, row in df.iterrows():
    color = 'green' if row['close'] >= row['open'] else 'red'
    
    # Cuerpo de la vela
    height = abs(row['close'] - row['open'])
    bottom = min(row['open'], row['close'])
    rect = Rectangle((i, bottom), 0.6, height, facecolor=color, edgecolor='black')
    ax.add_patch(rect)
    
    # Mecha (high-low)
    ax.plot([i + 0.3, i + 0.3], [row['low'], row['high']], color='black', linewidth=1)

# Agregar medias móviles
if df['sma_20'].notna().any():
    ax.plot(df.index, df['sma_20'], label='SMA-20', color='blue', linewidth=1.5)
if df['sma_50'].notna().any():
    ax.plot(df.index, df['sma_50'], label='SMA-50', color='orange', linewidth=1.5)

ax.set_xlabel('Días')
ax.set_ylabel('Precio ($)')
ax.set_title(f'Gráfico de Velas - {ticker}')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f'candlestick_{ticker}.png')
print(f"Gráfico guardado como candlestick_{ticker}.png")
```

### Respuesta esperada:
```json
[
  {
    "date": "2024-04-10",
    "open": 450.25,
    "high": 455.80,
    "low": 448.50,
    "close": 453.75,
    "volume": 3500000,
    "sma_20": 448.32,
    "sma_50": 445.67
  },
  ...
]
```

---

## 9. Generar reporte técnico en PDF

### cURL:
```bash
curl -X POST http://localhost:8000/reports/generate-pdf --output reporte_bvc.pdf
```

### Python:
```python
import requests

print("Generando reporte PDF (puede tardar 2-3 minutos)...")
response = requests.post("http://localhost:8000/reports/generate-pdf")

if response.status_code == 200:
    with open("reporte_bvc.pdf", "wb") as f:
        f.write(response.content)
    print("✅ Reporte generado: reporte_bvc.pdf")
else:
    print(f"❌ Error: {response.text}")
```

**Nota:** Este endpoint genera un PDF completo con:
- Portada
- Resumen ejecutivo
- Matriz de correlación (heatmap)
- Gráfico de volatilidad
- Tabla de clasificación de riesgo
- Conclusiones

---

## 10. Script completo de análisis

### Python - Análisis completo de un portafolio:
```python
import requests
import pandas as pd
import matplotlib.pyplot as plt

BASE_URL = "http://localhost:8000"

# 1. Obtener todos los activos
print("📊 Obteniendo activos...")
response = requests.get(f"{BASE_URL}/assets")
assets = response.json()
print(f"Total de activos: {len(assets)}")

# 2. Clasificación de riesgo
print("\n📈 Calculando volatilidad...")
response = requests.get(f"{BASE_URL}/volatility/all")
volatility = pd.DataFrame(response.json())

print("\nDistribución por riesgo:")
print(volatility['risk_level'].value_counts())

# 3. Comparar activos similares
print("\n🔍 Comparando VOO vs SPY...")
payload = {"ticker_a": "VOO", "ticker_b": "SPY"}
response = requests.post(f"{BASE_URL}/similarity/compare", json=payload)
similarity = response.json()
print(f"Correlación de Pearson: {similarity['pearson']:.6f}")

# 4. Análisis de patrones de un activo
print("\n📉 Analizando patrones de ECOPETROL.CL...")
response = requests.get(f"{BASE_URL}/patterns/ECOPETROL.CL")
patterns = response.json()
print(f"Volatilidad anual: {patterns['volatility_metrics']['annual_volatility']:.2f}%")
print(f"Clasificación: {patterns['risk_classification']}")

# 5. Generar reporte
print("\n📄 Generando reporte PDF...")
response = requests.post(f"{BASE_URL}/reports/generate-pdf")
if response.status_code == 200:
    with open("reporte_completo.pdf", "wb") as f:
        f.write(response.content)
    print("✅ Reporte generado: reporte_completo.pdf")

print("\n✅ Análisis completo finalizado")
```

---

## 11. Uso desde JavaScript/TypeScript

### Fetch API:
```javascript
// Obtener activos
async function getAssets() {
  const response = await fetch('http://localhost:8000/assets');
  const assets = await response.json();
  console.log('Total de activos:', assets.length);
  return assets;
}

// Comparar similitud
async function compareSimilarity(tickerA, tickerB) {
  const response = await fetch('http://localhost:8000/similarity/compare', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      ticker_a: tickerA,
      ticker_b: tickerB
    })
  });
  
  const result = await response.json();
  console.log(`Correlación ${tickerA} vs ${tickerB}:`, result.pearson);
  return result;
}

// Obtener volatilidad
async function getVolatility() {
  const response = await fetch('http://localhost:8000/volatility/all');
  const data = await response.json();
  
  // Filtrar por nivel de riesgo
  const agresivos = data.filter(a => a.risk_level === 'AGRESIVO');
  console.log('Activos agresivos:', agresivos.length);
  return data;
}

// Uso
getAssets();
compareSimilarity('VOO', 'SPY');
getVolatility();
```

---

## 12. Integración con Excel/CSV

### Python - Exportar datos a CSV:
```python
import requests
import pandas as pd

BASE_URL = "http://localhost:8000"

# Obtener clasificación de riesgo
response = requests.get(f"{BASE_URL}/volatility/all")
df = pd.DataFrame(response.json())

# Guardar a CSV
df.to_csv('clasificacion_riesgo.csv', index=False)
print("✅ Datos exportados a clasificacion_riesgo.csv")

# Obtener precios de un activo
ticker = "ECOPETROL.CL"
response = requests.get(f"{BASE_URL}/assets/{ticker}/prices")
prices_df = pd.DataFrame(response.json())

# Guardar a CSV
prices_df.to_csv(f'precios_{ticker}.csv', index=False)
print(f"✅ Precios exportados a precios_{ticker}.csv")
```

---

## Notas Importantes

### Tiempos de respuesta esperados:
- `/assets`: < 100ms
- `/assets/{ticker}/prices`: < 200ms
- `/similarity/compare`: 100-500ms (depende de la longitud de las series)
- `/similarity/correlation-matrix`: 1-2 minutos (calcula 22×22 = 484 correlaciones)
- `/patterns/{ticker}`: 200-500ms
- `/volatility/all`: 2-5 segundos
- `/candlestick/{ticker}`: < 300ms
- `/reports/generate-pdf`: 2-3 minutos (genera gráficos y PDF)

### Manejo de errores:
Todos los endpoints retornan códigos HTTP estándar:
- `200`: Éxito
- `400`: Petición inválida
- `404`: Recurso no encontrado
- `500`: Error del servidor

Ejemplo de manejo de errores en Python:
```python
import requests

try:
    response = requests.get("http://localhost:8000/assets/INVALID/prices")
    response.raise_for_status()  # Lanza excepción si status != 200
    data = response.json()
except requests.exceptions.HTTPError as e:
    print(f"Error HTTP: {e}")
    print(f"Detalle: {response.json()['detail']}")
except requests.exceptions.ConnectionError:
    print("Error: No se pudo conectar al servidor")
```

---

## Recursos Adicionales

- **Documentación interactiva:** http://localhost:8000/docs
- **Documentación alternativa:** http://localhost:8000/redoc
- **Health check:** http://localhost:8000/health
- **Suite de pruebas:** `python test_api.py`

---

**Última actualización:** Mayo 12, 2026
