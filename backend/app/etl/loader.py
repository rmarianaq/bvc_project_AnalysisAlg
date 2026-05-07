from app.core.database import get_connection


def create_unified_view():
    """
    Crea una vista en PostgreSQL que unifica todos los activos
    en una sola tabla alineada por fecha.

    La vista hace un PIVOT dinámico: cada activo se convierte
    en una columna con su precio de cierre.

    Usamos LEFT JOIN para que todas las fechas aparezcan
    aunque un activo no haya operado ese día (NULL).
    """
    conn   = get_connection()
    cursor = conn.cursor()

    # Primero obtenemos todos los tickers registrados
    cursor.execute("SELECT id, ticker FROM assets ORDER BY ticker;")
    assets = cursor.fetchall()

    if not assets:
        print("❌ No hay activos registrados")
        return

    # ─────────────────────────────────────────────────────
    # Construimos el SELECT dinámicamente
    # Para cada activo creamos una subconsulta que busca
    # su precio de cierre en cada fecha
    # ─────────────────────────────────────────────────────
    select_columns = []
    joins          = []

    for asset_id, ticker in assets:
        # Nombre seguro para usar como alias en SQL
        # Reemplazamos puntos y guiones por guiones bajos
        alias = ticker.replace(".", "_").replace("-", "_")

        # Columna del SELECT: precio de cierre de este activo
        select_columns.append(
            f'    {alias}.close_price AS "{ticker}"'
        )

        # LEFT JOIN con la tabla de precios filtrada por asset_id
        joins.append(f"""
    LEFT JOIN (
        SELECT trade_date, close_price
        FROM daily_prices
        WHERE asset_id = {asset_id}
    ) AS {alias} ON dates.trade_date = {alias}.trade_date""")

    # Unimos todas las partes del SELECT
    columns_sql = ",\n".join(select_columns)
    joins_sql   = "".join(joins)

    # ─────────────────────────────────────────────────────
    # La vista completa:
    # 1. Subquery "dates" obtiene todas las fechas únicas
    # 2. LEFT JOIN agrega el precio de cada activo por fecha
    # ─────────────────────────────────────────────────────
    view_sql = f"""
    CREATE OR REPLACE VIEW unified_prices AS
    SELECT
        dates.trade_date,
{columns_sql}
    FROM (
        SELECT DISTINCT trade_date
        FROM daily_prices
        ORDER BY trade_date
    ) AS dates
{joins_sql}
    ORDER BY dates.trade_date;
    """

    cursor.execute("DROP VIEW IF EXISTS unified_prices;")
    cursor.execute(view_sql)
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Vista unificada creada correctamente")


def get_unified_summary():
    """
    Muestra un resumen estadístico de la vista unificada.
    Útil para verificar que la unificación fue correcta.
    """
    conn   = get_connection()
    cursor = conn.cursor()

    # Total de fechas en la vista
    cursor.execute("SELECT COUNT(*) FROM unified_prices;")
    total_dates = cursor.fetchone()[0]

    # Rango de fechas
    cursor.execute("""
        SELECT MIN(trade_date), MAX(trade_date)
        FROM unified_prices;
    """)
    min_date, max_date = cursor.fetchone()

    # Total de activos
    cursor.execute("SELECT COUNT(*) FROM assets;")
    total_assets = cursor.fetchone()[0]

    # Total de registros en daily_prices
    cursor.execute("SELECT COUNT(*) FROM daily_prices;")
    total_records = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    print("\n" + "=" * 55)
    print("   RESUMEN DEL DATASET UNIFICADO")
    print("=" * 55)
    print(f"   Total activos      : {total_assets}")
    print(f"   Total registros    : {total_records:,}")
    print(f"   Fechas únicas      : {total_dates:,}")
    print(f"   Desde              : {min_date}")
    print(f"   Hasta              : {max_date}")
    print(f"   Días cubiertos     : {(max_date - min_date).days:,}")
    print("=" * 55)

def detect_calendar_gaps() -> dict:
    """
    Detecta fechas donde hay operaciones en algunos activos pero no en otros.
    Esto es normal: BVC tiene festivos distintos a NYSE.
    
    Estrategia adoptada: forward fill (propagar último precio conocido).
    Impacto algorítmico: las métricas de similitud del Req. 2 operarán sobre
    series de la misma longitud, eliminando sesgo por días no operados.
    Si se dejaran NULL, Pearson/DTW ignorarían esas posiciones, alterando
    la distancia calculada entre activos de distintos mercados.
    """
    conn   = get_connection()
    cursor = conn.cursor()

    # Fechas donde al menos un activo operó
    cursor.execute("SELECT DISTINCT trade_date FROM daily_prices ORDER BY trade_date;")
    all_dates = [row[0] for row in cursor.fetchall()]

    # Activos registrados
    cursor.execute("SELECT id, ticker FROM assets ORDER BY ticker;")
    assets = cursor.fetchall()

    gaps = {}  # ticker -> lista de fechas sin datos

    for asset_id, ticker in assets:
        cursor.execute(
            "SELECT trade_date FROM daily_prices WHERE asset_id = %s;",
            (asset_id,)
        )
        asset_dates = {row[0] for row in cursor.fetchall()}
        missing = [d for d in all_dates if d not in asset_dates]
        if missing:
            gaps[ticker] = missing

    cursor.close()
    conn.close()
    return {"total_dates": len(all_dates), "gaps": gaps}


def forward_fill_unified() -> int:
    """
    Para cada fecha sin precio en un activo, propaga el último
    precio de cierre conocido (forward fill).
    
    Esto alinea los calendarios bursátiles: si ECOPETROL.CL
    no operó el lunes festivo colombiano pero VOO sí,
    ECOPETROL.CL usará su último precio registrado.
    
    Retorna la cantidad de registros rellenados.
    """
    conn   = get_connection()
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


def run_loader():
    """
    Ejecuta la unificación completa del dataset.
    """
    print("=" * 55)
    print("   INICIANDO UNIFICACIÓN DEL DATASET")
    print("=" * 55)

    # 1. Crear la vista unificada
    create_unified_view()

    # 2. Mostrar resumen
    get_unified_summary()


    # ── Manejo de calendario bursátil ──────────────────────
    # 3. Detectar y reportar gaps por diferencias de calendario
    gap_report = detect_calendar_gaps()
    print(f"\n📅 Fechas únicas en el dataset: {gap_report['total_dates']:,}")
    print(f"   Activos con gaps de calendario: {len(gap_report['gaps'])}")
    for ticker, missing in gap_report["gaps"].items():
        print(f"   {ticker}: {len(missing)} días sin datos (BVC/NYSE holiday diff)")

    # 4. Aplicar forward fill para alinear las series
    filled = forward_fill_unified()
    print(f"\n✅ Forward fill aplicado: {filled} registros completados")
    print("   Estrategia: último precio conocido propagado hacia adelante")
    print("   Impacto: series alineadas para análisis de similitud (Req. 2)")

    print("\n✅ Requerimiento 1 completado exitosamente")


if __name__ == "__main__":
    run_loader()