from app.core.database import get_connection

def create_tables():
    """
    Crea todas las tablas necesarias en PostgreSQL.
    Se ejecuta una sola vez al iniciar el proyecto.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Tabla 1: Catálogo de activos
    # Guarda la información básica de cada acción o ETF
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id          SERIAL PRIMARY KEY,
            ticker      VARCHAR(20) UNIQUE NOT NULL,
            name        VARCHAR(100),
            market      VARCHAR(20),  -- 'BVC' o 'GLOBAL'
            asset_type  VARCHAR(20),  -- 'STOCK' o 'ETF'
            created_at  TIMESTAMP DEFAULT NOW()
        );
    """)

    # Tabla 2: Precios históricos diarios
    # Aquí se guardan todos los datos OHLCV de cada activo
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_prices (
            id          SERIAL PRIMARY KEY,
            asset_id    INTEGER REFERENCES assets(id),
            trade_date  DATE NOT NULL,
            open_price  NUMERIC(18, 6),
            high_price  NUMERIC(18, 6),
            low_price   NUMERIC(18, 6),
            close_price NUMERIC(18, 6),
            volume      BIGINT,
            UNIQUE(asset_id, trade_date)
        );
    """)

    # Tabla 3: Log del proceso ETL
    # Registra cada descarga: cuándo fue, cuántos registros, si hubo errores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS etl_log (
            id           SERIAL PRIMARY KEY,
            ticker       VARCHAR(20),
            status       VARCHAR(20),  -- 'SUCCESS', 'ERROR', 'PARTIAL'
            records      INTEGER,
            message      TEXT,
            executed_at  TIMESTAMP DEFAULT NOW()
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Tablas creadas correctamente")


if __name__ == "__main__":
    create_tables()