from app.core.database import get_connection


def get_returns(ticker: str) -> list:
    """
    Calcula los retornos diarios de un activo.
    
    Fórmula: r_t = (P_t - P_{t-1}) / P_{t-1}
    
    Usamos retornos en vez de precios para:
    - Eliminar diferencias de escala entre activos (COP vs USD)
    - Hacer las series comparables entre sí
    - Estabilizar la varianza de la serie temporal
    """
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT trade_date, close_price
        FROM daily_prices dp
        JOIN assets a ON dp.asset_id = a.id
        WHERE a.ticker = %s
          AND close_price IS NOT NULL
        ORDER BY trade_date ASC;
    """, (ticker,))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    returns = []
    for i in range(1, len(rows)):
        date     = rows[i][0]
        price    = float(rows[i][1])
        prev     = float(rows[i - 1][1])

        if prev != 0:
            r = (price - prev) / prev
            returns.append({"date": date, "return": r})

    return returns


def get_aligned_returns(ticker_a: str, ticker_b: str) -> tuple:
    """
    Retorna dos listas de retornos alineadas por fecha.
    Solo incluye fechas donde AMBOS activos tienen datos.
    
    Esto es necesario para que los algoritmos de similitud
    comparen exactamente los mismos períodos de tiempo.
    """
    returns_a = {r["date"]: r["return"] for r in get_returns(ticker_a)}
    returns_b = {r["date"]: r["return"] for r in get_returns(ticker_b)}

    # Fechas comunes a ambos activos
    common_dates = sorted(set(returns_a.keys()) & set(returns_b.keys()))

    series_a = [returns_a[d] for d in common_dates]
    series_b = [returns_b[d] for d in common_dates]

    return series_a, series_b, common_dates