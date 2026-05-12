"""
Requerimiento 3: Análisis de frecuencia de patrones y medición de volatilidad.

Este módulo implementa:
1. Algoritmo de ventanas deslizantes (sliding window) para detectar patrones
2. Cálculo de volatilidad histórica
3. Clasificación de activos por nivel de riesgo
"""

import math
from app.core.database import get_connection


def get_price_series(ticker: str) -> list:
    """
    Obtiene la serie de precios de cierre de un activo.
    Retorna lista de diccionarios con fecha y precio.
    """
    conn   = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT dp.trade_date, dp.close_price
        FROM daily_prices dp
        JOIN assets a ON dp.asset_id = a.id
        WHERE a.ticker = %s
          AND dp.close_price IS NOT NULL
        ORDER BY dp.trade_date ASC;
    """, (ticker,))
    
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return [
        {"date": row[0], "price": float(row[1])}
        for row in rows
    ]


def detect_consecutive_rises(prices: list, window_size: int = 3) -> dict:
    """
    Patrón 1: Secuencias de días consecutivos al alza.
    
    Algoritmo de ventana deslizante:
    - Recorre la serie de precios con una ventana de tamaño N
    - Detecta si todos los precios en la ventana son crecientes
    - Cuenta la frecuencia de este patrón
    
    Complejidad: O(n * w) donde n = longitud de la serie, w = tamaño de ventana
    
    Parámetros:
        prices: lista de diccionarios con 'date' y 'price'
        window_size: tamaño de la ventana (por defecto 3 días)
    
    Retorna:
        dict con frecuencia del patrón y posiciones donde ocurre
    """
    n = len(prices)
    if n < window_size:
        return {"frequency": 0, "occurrences": [], "total_windows": 0}
    
    occurrences = []
    
    # Ventana deslizante: recorremos desde 0 hasta n - window_size
    for i in range(n - window_size + 1):
        # Verificamos si todos los precios en la ventana son crecientes
        is_rising = True
        for j in range(i, i + window_size - 1):
            if prices[j + 1]["price"] <= prices[j]["price"]:
                is_rising = False
                break
        
        if is_rising:
            occurrences.append({
                "start_date": prices[i]["date"],
                "end_date": prices[i + window_size - 1]["date"],
                "start_price": prices[i]["price"],
                "end_price": prices[i + window_size - 1]["price"],
                "change_pct": ((prices[i + window_size - 1]["price"] - prices[i]["price"]) 
                              / prices[i]["price"] * 100)
            })
    
    total_windows = n - window_size + 1
    frequency = len(occurrences)
    
    return {
        "frequency": frequency,
        "occurrences": occurrences,
        "total_windows": total_windows,
        "frequency_pct": (frequency / total_windows * 100) if total_windows > 0 else 0
    }


def detect_volatility_spikes(prices: list, window_size: int = 5, threshold: float = 2.0) -> dict:
    """
    Patrón 2: Picos de volatilidad (volatility spikes).
    
    Detecta ventanas donde la desviación estándar de los retornos
    supera un umbral (threshold) veces la desviación estándar global.
    
    Formalización matemática:
    - Para cada ventana de tamaño w, calculamos σ_ventana
    - Si σ_ventana > threshold × σ_global, es un pico de volatilidad
    
    Complejidad: O(n * w)
    
    Parámetros:
        prices: lista de precios
        window_size: tamaño de la ventana (por defecto 5 días)
        threshold: multiplicador de la volatilidad global (por defecto 2.0)
    
    Retorna:
        dict con frecuencia de picos y sus posiciones
    """
    n = len(prices)
    if n < window_size + 1:
        return {"frequency": 0, "occurrences": [], "total_windows": 0}
    
    # Calcular retornos diarios
    returns = []
    for i in range(1, n):
        if prices[i - 1]["price"] != 0:
            r = (prices[i]["price"] - prices[i - 1]["price"]) / prices[i - 1]["price"]
            returns.append(r)
    
    if len(returns) < window_size:
        return {"frequency": 0, "occurrences": [], "total_windows": 0}
    
    # Calcular volatilidad global (desviación estándar de todos los retornos)
    mean_return = sum(returns) / len(returns)
    variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
    global_std = math.sqrt(variance)
    
    occurrences = []
    
    # Ventana deslizante sobre los retornos
    for i in range(len(returns) - window_size + 1):
        window_returns = returns[i:i + window_size]
        
        # Calcular desviación estándar de la ventana
        window_mean = sum(window_returns) / window_size
        window_variance = sum((r - window_mean) ** 2 for r in window_returns) / window_size
        window_std = math.sqrt(window_variance)
        
        # Detectar si es un pico de volatilidad
        if window_std > threshold * global_std:
            occurrences.append({
                "start_date": prices[i + 1]["date"],  # +1 porque returns empieza en índice 1
                "end_date": prices[i + window_size]["date"],
                "window_volatility": round(window_std * 100, 4),  # En porcentaje
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


def calculate_volatility(ticker: str, window: int = 252) -> dict:
    """
    Calcula métricas de volatilidad para un activo.
    
    Métricas calculadas:
    1. Volatilidad histórica (desviación estándar anualizada)
    2. Volatilidad móvil (últimos N días)
    3. Rango de precios (max - min) / promedio
    
    Fórmula de volatilidad anualizada:
        σ_anual = σ_diaria × sqrt(252)
    
    Donde 252 es el número aproximado de días de negociación al año.
    
    Complejidad: O(n)
    """
    prices = get_price_series(ticker)
    n = len(prices)
    
    if n < 2:
        return {
            "ticker": ticker,
            "error": "Datos insuficientes"
        }
    
    # Calcular retornos diarios
    returns = []
    for i in range(1, n):
        if prices[i - 1]["price"] != 0:
            r = (prices[i]["price"] - prices[i - 1]["price"]) / prices[i - 1]["price"]
            returns.append(r)
    
    if not returns:
        return {
            "ticker": ticker,
            "error": "No se pudieron calcular retornos"
        }
    
    # Volatilidad histórica (desviación estándar)
    mean_return = sum(returns) / len(returns)
    variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
    daily_std = math.sqrt(variance)
    
    # Anualizar la volatilidad (252 días de negociación al año)
    annual_volatility = daily_std * math.sqrt(252)
    
    # Volatilidad móvil (últimos N días)
    recent_window = min(window, len(returns))
    recent_returns = returns[-recent_window:]
    recent_mean = sum(recent_returns) / len(recent_returns)
    recent_variance = sum((r - recent_mean) ** 2 for r in recent_returns) / len(recent_returns)
    recent_std = math.sqrt(recent_variance)
    recent_annual = recent_std * math.sqrt(252)
    
    # Rango de precios
    price_values = [p["price"] for p in prices]
    max_price = max(price_values)
    min_price = min(price_values)
    avg_price = sum(price_values) / len(price_values)
    price_range_pct = ((max_price - min_price) / avg_price * 100) if avg_price > 0 else 0
    
    return {
        "ticker": ticker,
        "daily_volatility": round(daily_std * 100, 4),  # En porcentaje
        "annual_volatility": round(annual_volatility * 100, 2),  # En porcentaje
        "recent_volatility": round(recent_annual * 100, 2),  # Últimos N días
        "price_range_pct": round(price_range_pct, 2),
        "mean_return": round(mean_return * 100, 4),
        "data_points": len(returns)
    }


def classify_risk(annual_volatility: float) -> str:
    """
    Clasifica un activo según su nivel de riesgo basado en volatilidad anualizada.
    
    Criterios de clasificación:
    - Conservador: volatilidad < 15%
    - Moderado: 15% <= volatilidad < 25%
    - Agresivo: volatilidad >= 25%
    
    Estos umbrales son estándar en análisis financiero.
    """
    if annual_volatility < 15:
        return "CONSERVADOR"
    elif annual_volatility < 25:
        return "MODERADO"
    else:
        return "AGRESIVO"


def get_all_assets_volatility() -> list:
    """
    Calcula la volatilidad de todos los activos del portafolio
    y los clasifica por nivel de riesgo.
    
    Retorna lista ordenada por volatilidad descendente.
    """
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ticker FROM assets ORDER BY ticker;")
    tickers = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    
    results = []
    
    for ticker in tickers:
        vol_data = calculate_volatility(ticker)
        
        if "error" not in vol_data:
            risk_level = classify_risk(vol_data["annual_volatility"])
            results.append({
                "ticker": ticker,
                "annual_volatility": vol_data["annual_volatility"],
                "recent_volatility": vol_data["recent_volatility"],
                "risk_level": risk_level,
                "mean_return": vol_data["mean_return"]
            })
    
    # Ordenar por volatilidad descendente usando algoritmo manual
    # (Selection Sort para mantener consistencia con el proyecto)
    n = len(results)
    for i in range(n):
        max_idx = i
        for j in range(i + 1, n):
            if results[j]["annual_volatility"] > results[max_idx]["annual_volatility"]:
                max_idx = j
        results[i], results[max_idx] = results[max_idx], results[i]
    
    return results


def run_pattern_analysis(ticker: str) -> dict:
    """
    Ejecuta el análisis completo de patrones para un activo.
    
    Retorna:
    - Frecuencia de días consecutivos al alza
    - Frecuencia de picos de volatilidad
    - Métricas de volatilidad
    - Clasificación de riesgo
    """
    prices = get_price_series(ticker)
    
    if len(prices) < 5:
        return {
            "ticker": ticker,
            "error": "Datos insuficientes para análisis"
        }
    
    # Patrón 1: Días consecutivos al alza
    pattern1 = detect_consecutive_rises(prices, window_size=3)
    
    # Patrón 2: Picos de volatilidad
    pattern2 = detect_volatility_spikes(prices, window_size=5, threshold=2.0)
    
    # Volatilidad y clasificación
    volatility = calculate_volatility(ticker)
    
    if "error" not in volatility:
        risk_level = classify_risk(volatility["annual_volatility"])
    else:
        risk_level = "DESCONOCIDO"
    
    return {
        "ticker": ticker,
        "consecutive_rises": {
            "frequency": pattern1["frequency"],
            "frequency_pct": round(pattern1["frequency_pct"], 2),
            "total_windows": pattern1["total_windows"],
            "top_occurrences": pattern1["occurrences"][:5]  # Top 5
        },
        "volatility_spikes": {
            "frequency": pattern2["frequency"],
            "frequency_pct": round(pattern2["frequency_pct"], 2),
            "total_windows": pattern2["total_windows"],
            "global_volatility": pattern2["global_volatility"],
            "top_occurrences": pattern2["occurrences"][:5]  # Top 5
        },
        "volatility_metrics": volatility,
        "risk_classification": risk_level
    }


if __name__ == "__main__":
    # Ejemplo de uso
    print("=" * 70)
    print("   ANÁLISIS DE PATRONES Y VOLATILIDAD")
    print("=" * 70)
    
    # Análisis de un activo específico
    ticker = "ECOPETROL.CL"
    print(f"\n📊 Analizando {ticker}...")
    result = run_pattern_analysis(ticker)
    
    print(f"\n✅ Patrón 1: Días consecutivos al alza")
    print(f"   Frecuencia: {result['consecutive_rises']['frequency']} ocurrencias")
    print(f"   Porcentaje: {result['consecutive_rises']['frequency_pct']}%")
    
    print(f"\n✅ Patrón 2: Picos de volatilidad")
    print(f"   Frecuencia: {result['volatility_spikes']['frequency']} ocurrencias")
    print(f"   Porcentaje: {result['volatility_spikes']['frequency_pct']}%")
    
    print(f"\n✅ Volatilidad")
    print(f"   Anual: {result['volatility_metrics']['annual_volatility']}%")
    print(f"   Clasificación: {result['risk_classification']}")
    
    # Clasificación de todos los activos
    print("\n" + "=" * 70)
    print("   CLASIFICACIÓN DE RIESGO — TODOS LOS ACTIVOS")
    print("=" * 70)
    print(f"{'#':<4} {'Ticker':<18} {'Volatilidad':<14} {'Clasificación':<15} {'Retorno Medio'}")
    print("-" * 70)
    
    all_assets = get_all_assets_volatility()
    for i, asset in enumerate(all_assets, 1):
        print(
            f"{i:<4} {asset['ticker']:<18} "
            f"{asset['annual_volatility']:>6.2f}% {'':<6} "
            f"{asset['risk_level']:<15} "
            f"{asset['mean_return']:>6.4f}%"
        )
