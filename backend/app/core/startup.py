"""
Módulo de inicialización automática del sistema.

Este módulo se ejecuta al iniciar el servidor y verifica/crea automáticamente:
1. Tablas principales (assets, daily_prices, etl_log)
2. Tablas de caché (correlation_cache, volatility_cache, benchmark_cache)
3. Datos financieros (si no existen)
4. Datos pre-calculados en caché (si no existen)

Todo es idempotente: si ya existe, no lo vuelve a crear.
"""

import os
import sys
from app.core.database import get_connection


def check_table_exists(cursor, table_name: str) -> bool:
    """Verifica si una tabla existe en la base de datos."""
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = %s
        );
    """, (table_name,))
    return cursor.fetchone()[0]


def create_main_tables():
    """Crea las tablas principales si no existen."""
    conn = get_connection()
    cursor = conn.cursor()
    
    tables_created = []
    
    # Tabla 1: Catálogo de activos
    if not check_table_exists(cursor, 'assets'):
        cursor.execute("""
            CREATE TABLE assets (
                id          SERIAL PRIMARY KEY,
                ticker      VARCHAR(20) UNIQUE NOT NULL,
                name        VARCHAR(100),
                market      VARCHAR(20),
                asset_type  VARCHAR(20),
                created_at  TIMESTAMP DEFAULT NOW()
            );
        """)
        tables_created.append('assets')
    
    # Tabla 2: Precios históricos diarios
    if not check_table_exists(cursor, 'daily_prices'):
        cursor.execute("""
            CREATE TABLE daily_prices (
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
        tables_created.append('daily_prices')
    
    # Tabla 3: Log del proceso ETL
    if not check_table_exists(cursor, 'etl_log'):
        cursor.execute("""
            CREATE TABLE etl_log (
                id           SERIAL PRIMARY KEY,
                ticker       VARCHAR(20),
                status       VARCHAR(20),
                records      INTEGER,
                message      TEXT,
                executed_at  TIMESTAMP DEFAULT NOW()
            );
        """)
        tables_created.append('etl_log')
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return tables_created


def create_cache_tables():
    """Crea las tablas de caché si no existen."""
    conn = get_connection()
    cursor = conn.cursor()
    
    tables_created = []
    
    # Tabla de correlación
    if not check_table_exists(cursor, 'correlation_cache'):
        cursor.execute("""
            CREATE TABLE correlation_cache (
                ticker_a VARCHAR(20) NOT NULL,
                ticker_b VARCHAR(20) NOT NULL,
                correlation DECIMAL(10, 6) NOT NULL,
                calculated_at TIMESTAMP DEFAULT NOW(),
                PRIMARY KEY (ticker_a, ticker_b)
            );
        """)
        cursor.execute("""
            CREATE INDEX idx_correlation_ticker_a ON correlation_cache(ticker_a);
        """)
        cursor.execute("""
            CREATE INDEX idx_correlation_ticker_b ON correlation_cache(ticker_b);
        """)
        tables_created.append('correlation_cache')
    
    # Tabla de volatilidad
    if not check_table_exists(cursor, 'volatility_cache'):
        cursor.execute("""
            CREATE TABLE volatility_cache (
                ticker VARCHAR(20) PRIMARY KEY,
                annual_volatility DECIMAL(10, 4) NOT NULL,
                recent_volatility DECIMAL(10, 4) NOT NULL,
                risk_level VARCHAR(20) NOT NULL,
                mean_return DECIMAL(10, 6) NOT NULL,
                data_points INTEGER NOT NULL,
                calculated_at TIMESTAMP DEFAULT NOW()
            );
        """)
        cursor.execute("""
            CREATE INDEX idx_volatility_risk_level ON volatility_cache(risk_level);
        """)
        cursor.execute("""
            CREATE INDEX idx_volatility_annual ON volatility_cache(annual_volatility DESC);
        """)
        tables_created.append('volatility_cache')
    
    # Tabla de benchmark
    if not check_table_exists(cursor, 'benchmark_cache'):
        cursor.execute("""
            CREATE TABLE benchmark_cache (
                algorithm VARCHAR(50) PRIMARY KEY,
                time_seconds DECIMAL(10, 6) NOT NULL,
                records INTEGER NOT NULL,
                complexity VARCHAR(50),
                calculated_at TIMESTAMP DEFAULT NOW()
            );
        """)
        cursor.execute("""
            CREATE INDEX idx_benchmark_time ON benchmark_cache(time_seconds ASC);
        """)
        tables_created.append('benchmark_cache')
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return tables_created


def check_data_exists() -> dict:
    """Verifica qué datos existen en la base de datos."""
    conn = get_connection()
    cursor = conn.cursor()
    
    status = {
        'assets': 0,
        'prices': 0,
        'correlation_cache': 0,
        'volatility_cache': 0,
        'benchmark_cache': 0
    }
    
    # Verificar activos
    if check_table_exists(cursor, 'assets'):
        cursor.execute("SELECT COUNT(*) FROM assets;")
        status['assets'] = cursor.fetchone()[0]
    
    # Verificar precios
    if check_table_exists(cursor, 'daily_prices'):
        cursor.execute("SELECT COUNT(*) FROM daily_prices;")
        status['prices'] = cursor.fetchone()[0]
    
    # Verificar caché de correlación
    if check_table_exists(cursor, 'correlation_cache'):
        cursor.execute("SELECT COUNT(*) FROM correlation_cache;")
        status['correlation_cache'] = cursor.fetchone()[0]
    
    # Verificar caché de volatilidad
    if check_table_exists(cursor, 'volatility_cache'):
        cursor.execute("SELECT COUNT(*) FROM volatility_cache;")
        status['volatility_cache'] = cursor.fetchone()[0]
    
    # Verificar caché de benchmark
    if check_table_exists(cursor, 'benchmark_cache'):
        cursor.execute("SELECT COUNT(*) FROM benchmark_cache;")
        status['benchmark_cache'] = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    return status


def download_financial_data():
    """Descarga datos financieros si no existen."""
    print("📥 Descargando datos financieros...")
    print("   (Esto puede tardar 2-3 minutos)")
    
    try:
        from app.etl.extractor import run_etl
        run_etl()
        print("✅ Datos financieros descargados")
        return True
    except Exception as e:
        print(f"❌ Error al descargar datos: {e}")
        return False


def precompute_cache_data():
    """Pre-calcula datos de caché si no existen."""
    print("⚡ Pre-calculando datos de caché...")
    print("   (Esto puede tardar 1-2 minutos)")
    
    try:
        from app.cache.precompute import precompute_all
        precompute_all()
        print("✅ Datos de caché pre-calculados")
        return True
    except Exception as e:
        print(f"❌ Error al pre-calcular caché: {e}")
        return False


def initialize_system():
    """
    Inicializa el sistema completo de forma automática.
    
    Este método es idempotente: puede ejecutarse múltiples veces
    sin causar problemas. Solo crea/descarga lo que falta.
    """
    print("\n" + "="*60)
    print("🚀 INICIALIZANDO SISTEMA BVC ANALYSIS")
    print("="*60 + "\n")
    
    try:
        # Paso 1: Crear tablas principales
        print("📋 Verificando tablas principales...")
        main_tables = create_main_tables()
        if main_tables:
            print(f"✅ Tablas creadas: {', '.join(main_tables)}")
        else:
            print("✅ Tablas principales ya existen")
        
        # Paso 2: Crear tablas de caché
        print("\n📋 Verificando tablas de caché...")
        cache_tables = create_cache_tables()
        if cache_tables:
            print(f"✅ Tablas de caché creadas: {', '.join(cache_tables)}")
        else:
            print("✅ Tablas de caché ya existen")
        
        # Paso 3: Verificar datos
        print("\n📊 Verificando datos...")
        status = check_data_exists()
        
        print(f"   • Activos: {status['assets']}")
        print(f"   • Precios: {status['prices']}")
        print(f"   • Caché correlación: {status['correlation_cache']}")
        print(f"   • Caché volatilidad: {status['volatility_cache']}")
        print(f"   • Caché benchmark: {status['benchmark_cache']}")
        
        # Paso 4: Descargar datos si no existen
        if status['assets'] == 0 or status['prices'] == 0:
            print("\n📥 Datos financieros no encontrados")
            download_financial_data()
            # Actualizar status
            status = check_data_exists()
        else:
            print("\n✅ Datos financieros ya existen")
        
        # Paso 5: Pre-calcular caché si no existe
        cache_missing = (
            status['correlation_cache'] == 0 or
            status['volatility_cache'] == 0 or
            status['benchmark_cache'] == 0
        )
        
        if cache_missing and status['assets'] > 0:
            print("\n⚡ Datos de caché no encontrados")
            precompute_cache_data()
        elif status['assets'] > 0:
            print("\n✅ Datos de caché ya existen")
        
        print("\n" + "="*60)
        print("✅ SISTEMA INICIALIZADO CORRECTAMENTE")
        print("="*60 + "\n")
        
        # Mostrar resumen final
        final_status = check_data_exists()
        print("📊 Estado final:")
        print(f"   • {final_status['assets']} activos")
        print(f"   • {final_status['prices']} registros de precios")
        print(f"   • {final_status['correlation_cache']} correlaciones en caché")
        print(f"   • {final_status['volatility_cache']} volatilidades en caché")
        print(f"   • {final_status['benchmark_cache']} benchmarks en caché")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la inicialización: {e}")
        print("   El servidor continuará, pero algunas funciones pueden no estar disponibles.")
        return False


if __name__ == "__main__":
    initialize_system()
