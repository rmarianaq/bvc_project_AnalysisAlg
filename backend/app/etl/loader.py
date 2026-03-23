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

    print("\n✅ Requerimiento 1 completado exitosamente")


if __name__ == "__main__":
    run_loader()