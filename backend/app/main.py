"""
API REST con FastAPI para el proyecto de análisis algorítmico BVC.

Requerimiento 4: Dashboard bursátil y análisis visual.
Requerimiento 5: Despliegue como aplicación web.

Endpoints implementados:
- GET /assets: Lista todos los activos del portafolio
- GET /assets/{ticker}/prices: Obtiene precios históricos de un activo
- POST /similarity/compare: Compara dos activos con 4 algoritmos
- GET /similarity/correlation-matrix: Matriz de correlación de todos los activos
- GET /patterns/{ticker}: Análisis de patrones de un activo
- GET /volatility/all: Clasificación de riesgo de todos los activos
- GET /volatility/{ticker}: Volatilidad de un activo específico
- GET /candlestick/{ticker}: Datos para gráfico de velas con medias móviles
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import math

from app.core.database import get_connection
from app.similarity.returns import get_aligned_returns
from app.similarity.algorithms import (
    euclidean_distance, pearson_correlation,
    cosine_similarity, dtw_distance
)
from app.similarity.patterns import (
    run_pattern_analysis,
    get_all_assets_volatility,
    calculate_volatility
)
from app.api.reports import generate_pdf_report
from app.sorting.benchmark import run_benchmark, get_top_volume_days

app = FastAPI(
    title="BVC Analysis API",
    description="API para análisis algorítmico de activos financieros",
    version="1.0.0"
)

# Configurar CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════
# MODELOS PYDANTIC
# ═══════════════════════════════════════════════════════

class Asset(BaseModel):
    id: int
    ticker: str
    name: str
    market: str
    asset_type: str


class PriceData(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class SimilarityRequest(BaseModel):
    ticker_a: str
    ticker_b: str


class SimilarityResponse(BaseModel):
    ticker_a: str
    ticker_b: str
    common_dates: int
    date_from: str
    date_to: str
    euclidean: float
    pearson: float
    cosine: float
    dtw: float


class CorrelationMatrix(BaseModel):
    tickers: List[str]
    matrix: List[List[float]]


class VolatilityData(BaseModel):
    ticker: str
    annual_volatility: float
    recent_volatility: float
    risk_level: str
    mean_return: float


class CandlestickData(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None


# ═══════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════

@app.get("/")
def root():
    """Endpoint raíz con información de la API."""
    return {
        "message": "BVC Analysis API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "assets": "/assets",
            "similarity": "/similarity/compare",
            "correlation": "/similarity/correlation-matrix",
            "patterns": "/patterns/{ticker}",
            "volatility": "/volatility/all",
            "candlestick": "/candlestick/{ticker}",
            "sorting": "/sorting/benchmark",
            "top_volume": "/sorting/top-volume"
        }
    }


@app.get("/assets", response_model=List[Asset])
def get_assets():
    """
    Retorna la lista de todos los activos del portafolio.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, ticker, name, market, asset_type
        FROM assets
        ORDER BY ticker;
    """)
    
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return [
        {
            "id": row[0],
            "ticker": row[1],
            "name": row[2],
            "market": row[3],
            "asset_type": row[4]
        }
        for row in rows
    ]


@app.get("/assets/{ticker}/prices", response_model=List[PriceData])
def get_asset_prices(ticker: str, limit: Optional[int] = None):
    """
    Retorna los precios históricos de un activo.
    
    Parámetros:
    - ticker: símbolo del activo (ej: ECOPETROL.CL)
    - limit: número máximo de registros a retornar (opcional)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificar que el activo existe
    cursor.execute("SELECT id FROM assets WHERE ticker = %s;", (ticker,))
    asset = cursor.fetchone()
    
    if not asset:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail=f"Activo {ticker} no encontrado")
    
    asset_id = asset[0]
    
    # Obtener precios
    query = """
        SELECT trade_date, open_price, high_price, low_price, close_price, volume
        FROM daily_prices
        WHERE asset_id = %s
        ORDER BY trade_date DESC
    """
    
    if limit:
        query += f" LIMIT {limit}"
    
    cursor.execute(query, (asset_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return [
        {
            "date": str(row[0]),
            "open": float(row[1]) if row[1] else 0.0,
            "high": float(row[2]) if row[2] else 0.0,
            "low": float(row[3]) if row[3] else 0.0,
            "close": float(row[4]) if row[4] else 0.0,
            "volume": int(row[5]) if row[5] else 0
        }
        for row in rows
    ]


@app.post("/similarity/compare", response_model=SimilarityResponse)
def compare_similarity(request: SimilarityRequest):
    """
    Compara dos activos usando 4 algoritmos de similitud:
    - Distancia euclidiana
    - Correlación de Pearson
    - Similitud por coseno
    - Dynamic Time Warping (DTW)
    
    Complejidad:
    - Euclidiana, Pearson, Coseno: O(n)
    - DTW: O(n²)
    """
    try:
        series_a, series_b, dates = get_aligned_returns(
            request.ticker_a,
            request.ticker_b
        )
        
        if len(dates) < 2:
            raise HTTPException(
                status_code=400,
                detail="No hay suficientes fechas comunes entre los activos"
            )
        
        # Calcular las 4 métricas de similitud
        euclidean = euclidean_distance(series_a, series_b)
        pearson = pearson_correlation(series_a, series_b)
        cosine = cosine_similarity(series_a, series_b)
        dtw = dtw_distance(series_a, series_b)
        
        return {
            "ticker_a": request.ticker_a,
            "ticker_b": request.ticker_b,
            "common_dates": len(dates),
            "date_from": str(dates[0]),
            "date_to": str(dates[-1]),
            "euclidean": round(euclidean, 6),
            "pearson": round(pearson, 6),
            "cosine": round(cosine, 6),
            "dtw": round(dtw, 6)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/similarity/correlation-matrix", response_model=CorrelationMatrix)
def get_correlation_matrix():
    """
    Calcula la matriz de correlación de Pearson entre todos los activos.
    
    Esta matriz se usa para generar el heatmap del Requerimiento 4.
    
    Complejidad: O(n² × m) donde n = número de activos, m = longitud de series
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT ticker FROM assets ORDER BY ticker;")
    tickers = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    
    n = len(tickers)
    matrix = [[0.0] * n for _ in range(n)]
    
    # Calcular correlación entre cada par de activos
    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i][j] = 1.0  # Correlación consigo mismo = 1
            elif i < j:
                try:
                    series_a, series_b, _ = get_aligned_returns(tickers[i], tickers[j])
                    if len(series_a) > 1:
                        corr = pearson_correlation(series_a, series_b)
                        matrix[i][j] = round(corr, 4)
                        matrix[j][i] = round(corr, 4)  # Matriz simétrica
                except:
                    matrix[i][j] = 0.0
                    matrix[j][i] = 0.0
    
    return {
        "tickers": tickers,
        "matrix": matrix
    }


@app.get("/patterns/{ticker}")
def get_pattern_analysis(ticker: str):
    """
    Ejecuta el análisis completo de patrones para un activo.
    
    Requerimiento 3:
    - Patrón 1: Días consecutivos al alza (ventana deslizante)
    - Patrón 2: Picos de volatilidad
    - Métricas de volatilidad
    - Clasificación de riesgo
    """
    try:
        result = run_pattern_analysis(ticker)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/volatility/all", response_model=List[VolatilityData])
def get_all_volatility():
    """
    Retorna la clasificación de riesgo de todos los activos
    ordenados por volatilidad descendente.
    
    Requerimiento 3: Clasificación en conservadores, moderados y agresivos.
    """
    try:
        results = get_all_assets_volatility()
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/volatility/{ticker}")
def get_asset_volatility(ticker: str):
    """
    Retorna las métricas de volatilidad de un activo específico.
    """
    try:
        result = calculate_volatility(ticker)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/candlestick/{ticker}", response_model=List[CandlestickData])
def get_candlestick_data(ticker: str, days: Optional[int] = 180):
    """
    Retorna datos para gráfico de velas (candlestick) con medias móviles.
    
    Requerimiento 4: Gráficos de velas con medias móviles simples (SMA).
    
    Calcula:
    - SMA 20 días (media móvil simple de 20 períodos)
    - SMA 50 días (media móvil simple de 50 períodos)
    
    Complejidad: O(n × w) donde w = tamaño de ventana de la media móvil
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificar que el activo existe
    cursor.execute("SELECT id FROM assets WHERE ticker = %s;", (ticker,))
    asset = cursor.fetchone()
    
    if not asset:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail=f"Activo {ticker} no encontrado")
    
    asset_id = asset[0]
    
    # Obtener precios (necesitamos más datos para calcular las SMAs)
    cursor.execute("""
        SELECT trade_date, open_price, high_price, low_price, close_price, volume
        FROM daily_prices
        WHERE asset_id = %s
        ORDER BY trade_date ASC;
    """, (asset_id,))
    
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if not rows:
        raise HTTPException(status_code=404, detail="No hay datos de precios")
    
    # Convertir a lista de diccionarios
    prices = [
        {
            "date": str(row[0]),
            "open": float(row[1]) if row[1] else 0.0,
            "high": float(row[2]) if row[2] else 0.0,
            "low": float(row[3]) if row[3] else 0.0,
            "close": float(row[4]) if row[4] else 0.0,
            "volume": int(row[5]) if row[5] else 0
        }
        for row in rows
    ]
    
    # Calcular medias móviles simples (SMA)
    def calculate_sma(data: list, window: int) -> list:
        """
        Calcula la media móvil simple.
        Algoritmo de ventana deslizante: O(n)
        """
        sma = []
        for i in range(len(data)):
            if i < window - 1:
                sma.append(None)  # No hay suficientes datos
            else:
                window_data = data[i - window + 1:i + 1]
                avg = sum(p["close"] for p in window_data) / window
                sma.append(round(avg, 2))
        return sma
    
    sma_20 = calculate_sma(prices, 20)
    sma_50 = calculate_sma(prices, 50)
    
    # Agregar las SMAs a los datos
    for i, price in enumerate(prices):
        price["sma_20"] = sma_20[i]
        price["sma_50"] = sma_50[i]
    
    # Retornar solo los últimos N días solicitados
    return prices[-days:]


@app.get("/health")
def health_check():
    """Endpoint para verificar que la API está funcionando."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM assets;")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "assets_count": count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.post("/reports/generate-pdf")
def generate_report():
    """
    Genera un reporte técnico completo en formato PDF.
    
    Requerimiento 4: Exportación de reporte técnico en PDF que consolide
    los análisis visuales y numéricos realizados.
    
    El reporte incluye:
    - Resumen ejecutivo con estadísticas del dataset
    - Matriz de correlación (heatmap)
    - Clasificación de riesgo por volatilidad
    - Conclusiones del análisis
    """
    try:
        from fastapi.responses import FileResponse
        import os
        
        # Generar el PDF
        pdf_filename = generate_pdf_report()
        
        # Verificar que el archivo existe
        if not os.path.exists(pdf_filename):
            raise HTTPException(status_code=500, detail="Error al generar el PDF")
        
        # Retornar el archivo para descarga
        return FileResponse(
            path=pdf_filename,
            filename=pdf_filename,
            media_type="application/pdf"
        )
    
    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Dependencias faltantes: {str(e)}. Instalar con: pip install reportlab matplotlib seaborn"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sorting/benchmark")
def get_sorting_benchmark():
    """
    Ejecuta el benchmark de 12 algoritmos de ordenamiento sobre el dataset completo.
    
    Requerimiento 2: Análisis comparativo de algoritmos de ordenamiento.
    
    Ordena los registros por:
    1. Fecha de cotización (ascendente)
    2. Precio de cierre (desempate)
    
    Retorna los tiempos de ejecución de cada algoritmo.
    """
    try:
        results = run_benchmark()
        return {
            "results": results,
            "total_algorithms": len(results),
            "dataset_size": results[0]["records"] if results else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sorting/top-volume")
def get_top_volume(limit: int = 15):
    """
    Retorna los días con mayor volumen de negociación.
    
    Requerimiento 2: Top 15 días con mayor volumen ordenados de manera ascendente.
    
    Parámetros:
    - limit: número de registros a retornar (default: 15)
    """
    try:
        top_days = get_top_volume_days(limit)
        return {
            "top_volume_days": top_days,
            "count": len(top_days)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
