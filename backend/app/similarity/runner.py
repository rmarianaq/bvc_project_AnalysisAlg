from app.similarity.returns import get_aligned_returns
from app.similarity.algorithms import (
    euclidean_distance, pearson_correlation,
    cosine_similarity, dtw_distance
)


def compare_assets(ticker_a: str, ticker_b: str):
    """
    Compara dos activos usando los 4 algoritmos de similitud.
    """
    print(f"\n{'='*55}")
    print(f"   SIMILITUD: {ticker_a} vs {ticker_b}")
    print(f"{'='*55}")

    series_a, series_b, dates = get_aligned_returns(ticker_a, ticker_b)

    print(f"   Fechas comunes    : {len(dates)}")
    print(f"   Desde             : {dates[0]}")
    print(f"   Hasta             : {dates[-1]}")
    print(f"{'-'*55}")

    print(f"   Euclidiana        : {euclidean_distance(series_a, series_b):.6f}")
    print(f"   Pearson           : {pearson_correlation(series_a, series_b):.6f}")
    print(f"   Coseno            : {cosine_similarity(series_a, series_b):.6f}")

    # DTW es O(n²) — puede tardar con series largas
    print(f"   DTW               : calculando...", end=" ", flush=True)
    dtw = dtw_distance(series_a, series_b)
    print(f"{dtw:.6f}")

    print(f"{'='*55}")


if __name__ == "__main__":
    # Par de validación: deben tener similitud muy alta
    compare_assets("VOO", "SPY")

    # Par interesante: acción colombiana vs ETF global
    compare_assets("ECOPETROL.CL", "XLE")