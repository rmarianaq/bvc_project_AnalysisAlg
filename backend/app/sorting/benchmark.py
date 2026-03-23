import time
from app.core.database import get_connection
from app.sorting.algorithms import (
    selection_sort, gnome_sort, binary_insertion_sort,
    quicksort, heapsort, timsort, comb_sort, tree_sort,
    bucket_sort, pigeonhole_sort, radix_sort, bitonic_sort
)


def get_data_for_sorting() -> list:
    """
    Obtiene todos los registros del dataset unificado
    para ordenar por fecha y precio de cierre.
    """
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT dp.trade_date, dp.close_price, a.ticker
        FROM daily_prices dp
        JOIN assets a ON dp.asset_id = a.id
        ORDER BY dp.trade_date ASC;
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [
        {
            "trade_date":  row[0],
            "close_price": float(row[1]) if row[1] else 0.0,
            "ticker":      row[2]
        }
        for row in rows
    ]


def get_top_volume_days(top_n: int = 15) -> list:
    """
    Retorna los top N días con mayor volumen de negociación
    usando únicamente estructuras básicas (sin ORDER BY de SQL).

    Implementamos Selection Sort manualmente sobre los volúmenes
    para cumplir con el requisito de implementación explícita.
    """
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT dp.trade_date, a.ticker, dp.volume, dp.close_price
        FROM daily_prices dp
        JOIN assets a ON dp.asset_id = a.id
        WHERE dp.volume IS NOT NULL AND dp.volume > 0;
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    records = [
        {
            "trade_date":  row[0],
            "ticker":      row[1],
            "volume":      int(row[2]),
            "close_price": float(row[3]) if row[3] else 0.0
        }
        for row in rows
    ]

    # Ordenamos manualmente por volumen descendente
    # usando Selection Sort para mayor claridad algorítmica
    n = len(records)
    for i in range(min(top_n, n)):
        max_idx = i
        for j in range(i + 1, n):
            if records[j]["volume"] > records[max_idx]["volume"]:
                max_idx = j
        records[i], records[max_idx] = records[max_idx], records[i]

    return records[:top_n]


def run_benchmark() -> list:
    """
    Ejecuta los 12 algoritmos sobre el mismo dataset
    y mide el tiempo de cada uno.
    Retorna lista de resultados ordenada por tiempo.
    """
    print("=" * 55)
    print("   BENCHMARK — 12 ALGORITMOS DE ORDENAMIENTO")
    print("=" * 55)

    data = get_data_for_sorting()
    print(f"\n📊 Dataset: {len(data):,} registros\n")

    algorithms = [
        ("TimSort",              timsort),
        ("Comb Sort",            comb_sort),
        ("Selection Sort",       selection_sort),
        ("Tree Sort",            tree_sort),
        ("Pigeonhole Sort",      pigeonhole_sort),
        ("Bucket Sort",          bucket_sort),
        ("QuickSort",            quicksort),
        ("HeapSort",             heapsort),
        ("Bitonic Sort",         bitonic_sort),
        ("Gnome Sort",           gnome_sort),
        ("Binary Insertion Sort",binary_insertion_sort),
        ("RadixSort",            radix_sort),
    ]

    results = []

    for name, func in algorithms:
        print(f"⏱  Ejecutando {name}...", end=" ", flush=True)
        start   = time.perf_counter()
        sorted_data = func(data)
        elapsed = time.perf_counter() - start

        results.append({
            "algorithm": name,
            "time_seconds": round(elapsed, 4),
            "records": len(sorted_data)
        })
        print(f"{elapsed:.4f}s")

    # Ordenamos resultados por tiempo ascendente
    results.sort(key=lambda x: x["time_seconds"])

    print("\n" + "=" * 55)
    print("   RESULTADOS ORDENADOS POR TIEMPO")
    print("=" * 55)
    print(f"{'#':<4} {'Algoritmo':<25} {'Tiempo (s)':<12} {'Complejidad'}")
    print("-" * 55)

    complexity = {
        "TimSort":               "O(n log n)",
        "Comb Sort":             "O(n log n)",
        "Selection Sort":        "O(n²)",
        "Tree Sort":             "O(n log n)",
        "Pigeonhole Sort":       "O(n + k)",
        "Bucket Sort":           "O(n + k)",
        "QuickSort":             "O(n log n)",
        "HeapSort":              "O(n log n)",
        "Bitonic Sort":          "O(n log²n)",
        "Gnome Sort":            "O(n²)",
        "Binary Insertion Sort": "O(n²)",
        "RadixSort":             "O(nk)",
    }

    for i, r in enumerate(results, 1):
        comp = complexity[r["algorithm"]]
        print(f"{i:<4} {r['algorithm']:<25} {r['time_seconds']:<12} {comp}")

    # Top 15 días con mayor volumen
    print("\n" + "=" * 55)
    print("   TOP 15 DÍAS CON MAYOR VOLUMEN DE NEGOCIACIÓN")
    print("=" * 55)
    print(f"{'#':<4} {'Fecha':<14} {'Ticker':<15} {'Volumen':>15} {'Cierre':>10}")
    print("-" * 55)

    top_days = get_top_volume_days(15)
    for i, day in enumerate(top_days, 1):
        print(
            f"{i:<4} {str(day['trade_date']):<14} "
            f"{day['ticker']:<15} "
            f"{day['volume']:>15,} "
            f"{day['close_price']:>10.2f}"
        )

    return results


if __name__ == "__main__":
    run_benchmark()