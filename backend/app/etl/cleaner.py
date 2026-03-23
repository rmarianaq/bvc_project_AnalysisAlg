from app.core.database import get_connection

def get_all_assets():
    """
    Retorna la lista de todos los activos registrados en la BD.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, ticker FROM assets ORDER BY ticker;")
    assets = cursor.fetchall()
    cursor.close()
    conn.close()
    return assets


def get_prices_by_asset(asset_id: int) -> list:
    """
    Retorna todos los precios de un activo ordenados por fecha.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, trade_date, open_price, high_price,
               low_price, close_price, volume
        FROM daily_prices
        WHERE asset_id = %s
        ORDER BY trade_date ASC;
    """, (asset_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # Convertimos a lista de diccionarios para trabajar más fácil
    prices = []
    for row in rows:
        prices.append({
            "id":         row[0],
            "date":       row[1],
            "open":       float(row[2]) if row[2] is not None else None,
            "high":       float(row[3]) if row[3] is not None else None,
            "low":        float(row[4]) if row[4] is not None else None,
            "close":      float(row[5]) if row[5] is not None else None,
            "volume":     int(row[6])   if row[6] is not None else None
        })
    return prices


def detect_anomalies(prices: list) -> dict:
    """
    Detecta problemas en la serie de tiempo de un activo.
    Retorna un reporte con todos los problemas encontrados.
    """
    nulls        = []  # Filas con valores None
    negatives    = []  # Precios negativos o cero (imposibles)
    zero_volume  = []  # Días sin volumen de negociación
    duplicates   = []  # Fechas repetidas

    seen_dates = {}

    for i, price in enumerate(prices):
        date = str(price["date"])

        # 1. Detectar duplicados
        if date in seen_dates:
            duplicates.append(i)
        else:
            seen_dates[date] = i

        # 2. Detectar valores nulos
        for field in ["open", "high", "low", "close", "volume"]:
            if price[field] is None:
                nulls.append({"index": i, "date": date, "field": field})

        # 3. Detectar precios negativos o cero
        for field in ["open", "high", "low", "close"]:
            if price[field] is not None and price[field] <= 0:
                negatives.append({"index": i, "date": date, "field": field})

        # 4. Detectar volumen cero
        if price["volume"] is not None and price["volume"] == 0:
            zero_volume.append({"index": i, "date": date})

    return {
        "nulls":       nulls,
        "negatives":   negatives,
        "zero_volume": zero_volume,
        "duplicates":  duplicates
    }


def interpolate_linear(prices: list, index: int, field: str) -> float:
    """
    Aplica interpolación lineal para estimar un valor faltante.

    Busca el valor anterior y siguiente no nulo en la serie
    y calcula el punto medio proporcional.

    Fórmula:
        valor = v_ant + (v_sig - v_ant) × (pos / total_gaps)

    Solo interpola si el gap es de máximo 2 días consecutivos.
    Si el gap es mayor, retorna None para indicar que se debe eliminar.
    """
    # Buscar valor anterior no nulo
    prev_val  = None
    prev_dist = 0
    for i in range(index - 1, -1, -1):
        if prices[i][field] is not None and prices[i][field] > 0:
            prev_val  = prices[i][field]
            prev_dist = index - i
            break

    # Buscar valor siguiente no nulo
    next_val  = None
    next_dist = 0
    for i in range(index + 1, len(prices)):
        if prices[i][field] is not None and prices[i][field] > 0:
            next_val  = prices[i][field]
            next_dist = i - index
            break

    # Si el gap es mayor a 2, no interpolamos
    if prev_dist > 2 or next_dist > 2:
        return None

    # Si no hay valores anterior o siguiente, no podemos interpolar
    if prev_val is None or next_val is None:
        return None

    # Aplicar fórmula de interpolación lineal
    total_gap   = prev_dist + next_dist
    interpolated = prev_val + (next_val - prev_val) * (prev_dist / total_gap)
    return round(interpolated, 6)


def update_price_field(record_id: int, field: str, value: float):
    """
    Actualiza un campo específico de un registro en la BD.
    """
    # Mapeamos el nombre del campo al nombre de la columna en BD
    column_map = {
        "open":   "open_price",
        "high":   "high_price",
        "low":    "low_price",
        "close":  "close_price",
        "volume": "volume"
    }
    column = column_map[field]
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE daily_prices SET {column} = %s WHERE id = %s;",
        (value, record_id)
    )
    conn.commit()
    cursor.close()
    conn.close()


def delete_price(record_id: int):
    """
    Elimina un registro de la BD por su id.
    Se usa cuando el dato no puede ser corregido.
    """
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM daily_prices WHERE id = %s;", (record_id,))
    conn.commit()
    cursor.close()
    conn.close()


def clean_asset(asset_id: int, ticker: str) -> dict:
    """
    Limpia la serie de tiempo de un activo aplicando:
    1. Eliminación de duplicados
    2. Interpolación lineal para nulos aislados (gap <= 2)
    3. Eliminación de registros con gaps grandes (gap > 2)
    4. Eliminación de precios negativos o cero
    """
    prices  = get_prices_by_asset(asset_id)
    report  = detect_anomalies(prices)

    fixed   = 0
    deleted = 0

    # 1. Eliminar duplicados (conservamos el primero)
    for idx in report["duplicates"]:
        delete_price(prices[idx]["id"])
        deleted += 1

    # 2. Tratar valores nulos
    for null_info in report["nulls"]:
        idx   = null_info["index"]
        field = null_info["field"]
        price = prices[idx]

        if field == "volume":
            # Volumen nulo → asignamos 0 (día sin negociación)
            update_price_field(price["id"], "volume", 0)
            fixed += 1
        else:
            # Precio nulo → intentamos interpolación lineal
            interpolated = interpolate_linear(prices, idx, field)
            if interpolated is not None:
                update_price_field(price["id"], field, interpolated)
                fixed += 1
            else:
                # Gap muy grande → eliminamos el registro
                delete_price(price["id"])
                deleted += 1

    # 3. Eliminar precios negativos o cero (físicamente imposibles)
    for neg_info in report["negatives"]:
        idx = neg_info["index"]
        delete_price(prices[idx]["id"])
        deleted += 1

    return {
        "ticker":   ticker,
        "total":    len(prices),
        "nulls":    len(report["nulls"]),
        "dupes":    len(report["duplicates"]),
        "negatives":len(report["negatives"]),
        "fixed":    fixed,
        "deleted":  deleted
    }


def run_cleaning():
    """
    Ejecuta la limpieza sobre todos los activos del portafolio.
    """
    print("=" * 55)
    print("   INICIANDO LIMPIEZA DE DATOS")
    print("=" * 55)

    assets         = get_all_assets()
    total_fixed    = 0
    total_deleted  = 0
    total_nulls    = 0
    total_dupes    = 0

    for asset_id, ticker in assets:
        result = clean_asset(asset_id, ticker)

        status = "✅ Limpio"
        if result["nulls"] > 0 or result["dupes"] > 0 or result["negatives"] > 0:
            status = "🔧 Corregido"

        print(f"\n{status} {ticker}")
        print(f"   Total registros : {result['total']}")
        print(f"   Nulos detectados: {result['nulls']}")
        print(f"   Duplicados      : {result['dupes']}")
        print(f"   Negativos       : {result['negatives']}")
        print(f"   Interpolados    : {result['fixed']}")
        print(f"   Eliminados      : {result['deleted']}")

        total_fixed   += result["fixed"]
        total_deleted += result["deleted"]
        total_nulls   += result["nulls"]
        total_dupes   += result["dupes"]

    print("\n" + "=" * 55)
    print(f"   LIMPIEZA COMPLETADA")
    print(f"   Nulos encontrados : {total_nulls}")
    print(f"   Duplicados        : {total_dupes}")
    print(f"   Registros fijados : {total_fixed}")
    print(f"   Registros borrados: {total_deleted}")
    print("=" * 55)


if __name__ == "__main__":
    run_cleaning()