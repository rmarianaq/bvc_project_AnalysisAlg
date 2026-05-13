-- ═══════════════════════════════════════════════════════════════
-- Script para crear tablas de caché
-- Ejecutar: psql -U postgres -d bvc_analysis -f create_cache_tables.sql
-- ═══════════════════════════════════════════════════════════════

-- Tabla para matriz de correlación pre-calculada
CREATE TABLE IF NOT EXISTS correlation_cache (
    ticker_a VARCHAR(20) NOT NULL,
    ticker_b VARCHAR(20) NOT NULL,
    correlation DECIMAL(10, 6) NOT NULL,
    calculated_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (ticker_a, ticker_b)
);

-- Índices para búsquedas rápidas
CREATE INDEX IF NOT EXISTS idx_correlation_ticker_a ON correlation_cache(ticker_a);
CREATE INDEX IF NOT EXISTS idx_correlation_ticker_b ON correlation_cache(ticker_b);

-- Comentarios
COMMENT ON TABLE correlation_cache IS 'Matriz de correlación de Pearson pre-calculada entre todos los activos';
COMMENT ON COLUMN correlation_cache.ticker_a IS 'Ticker del primer activo';
COMMENT ON COLUMN correlation_cache.ticker_b IS 'Ticker del segundo activo';
COMMENT ON COLUMN correlation_cache.correlation IS 'Coeficiente de correlación de Pearson [-1, 1]';
COMMENT ON COLUMN correlation_cache.calculated_at IS 'Fecha y hora del cálculo';


-- Tabla para volatilidad pre-calculada
CREATE TABLE IF NOT EXISTS volatility_cache (
    ticker VARCHAR(20) PRIMARY KEY,
    annual_volatility DECIMAL(10, 4) NOT NULL,
    recent_volatility DECIMAL(10, 4) NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    mean_return DECIMAL(10, 6) NOT NULL,
    data_points INTEGER NOT NULL,
    calculated_at TIMESTAMP DEFAULT NOW()
);

-- Índice para búsquedas por nivel de riesgo
CREATE INDEX IF NOT EXISTS idx_volatility_risk_level ON volatility_cache(risk_level);
CREATE INDEX IF NOT EXISTS idx_volatility_annual ON volatility_cache(annual_volatility DESC);

-- Comentarios
COMMENT ON TABLE volatility_cache IS 'Métricas de volatilidad y clasificación de riesgo pre-calculadas';
COMMENT ON COLUMN volatility_cache.ticker IS 'Ticker del activo';
COMMENT ON COLUMN volatility_cache.annual_volatility IS 'Volatilidad anualizada (%)';
COMMENT ON COLUMN volatility_cache.recent_volatility IS 'Volatilidad de últimos 30 días (%)';
COMMENT ON COLUMN volatility_cache.risk_level IS 'Clasificación: CONSERVADOR, MODERADO, AGRESIVO';
COMMENT ON COLUMN volatility_cache.mean_return IS 'Retorno medio diario (%)';
COMMENT ON COLUMN volatility_cache.data_points IS 'Número de días analizados';


-- Tabla para benchmark de ordenamiento pre-calculado
CREATE TABLE IF NOT EXISTS benchmark_cache (
    algorithm VARCHAR(50) PRIMARY KEY,
    time_seconds DECIMAL(10, 6) NOT NULL,
    records INTEGER NOT NULL,
    complexity VARCHAR(50),
    calculated_at TIMESTAMP DEFAULT NOW()
);

-- Índice para ordenar por tiempo
CREATE INDEX IF NOT EXISTS idx_benchmark_time ON benchmark_cache(time_seconds ASC);

-- Comentarios
COMMENT ON TABLE benchmark_cache IS 'Resultados del benchmark de algoritmos de ordenamiento';
COMMENT ON COLUMN benchmark_cache.algorithm IS 'Nombre del algoritmo de ordenamiento';
COMMENT ON COLUMN benchmark_cache.time_seconds IS 'Tiempo de ejecución en segundos';
COMMENT ON COLUMN benchmark_cache.records IS 'Número de registros ordenados';
COMMENT ON COLUMN benchmark_cache.complexity IS 'Complejidad algorítmica (ej: O(n log n))';


-- Verificar que las tablas se crearon correctamente
SELECT 
    'correlation_cache' as tabla,
    COUNT(*) as registros
FROM correlation_cache
UNION ALL
SELECT 
    'volatility_cache' as tabla,
    COUNT(*) as registros
FROM volatility_cache
UNION ALL
SELECT 
    'benchmark_cache' as tabla,
    COUNT(*) as registros
FROM benchmark_cache;

-- Mostrar estructura de las tablas
\d correlation_cache
\d volatility_cache
\d benchmark_cache

PRINT '✅ Tablas de caché creadas exitosamente';
