"""
Script para pre-calcular y cachear datos que no cambian.

Ejecutar con:
    python -m app.cache.precompute

O desde el directorio backend:
    cd backend
    python -m app.cache.precompute
"""

import sys
import time
from datetime import datetime

from app.core.database import get_connection
from app.similarity.returns import get_aligned_returns
from app.similarity.algorithms import pearson_correlation
from app.similarity.patterns import get_all_assets_volatility
from app.sorting.benchmark import run_benchmark


def save_correlation_matrix():
    """
    Calcula y guarda la matriz de correlación completa.
    
    Complejidad: O(n² × m) donde n = número de activos, m = longitud de series
    
    Para 22 activos: 22 × 22 = 484 correlaciones a calcular
    (Solo calculamos 253 por simetría: n × (n+1) / 2)
    """
    print("\n" + "="*60)
    print("📊 CALCULANDO MATRIZ DE CORRELACIÓN")
    print("="*60)
    
    start_time = time.time()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Obtener todos los tickers
    cursor.execute("SELECT ticker FROM assets ORDER BY ticker;")
    tickers = [row[0] for row in cursor.fetchall()]
    
    print(f"📈 Activos a procesar: {len(tickers)}")
    print(f"🔢 Correlaciones a calcular: {len(tickers) * (len(tickers) + 1) // 2}")
    
    total_correlations = 0
    successful = 0
    failed = 0
    
    # Calcular correlaciones
    for i, ticker_a in enumerate(tickers):
        for j, ticker_b in enumerate(tickers):
            if i <= j:  # Solo calcular mitad superior (matriz simétrica)
                try:
                    if i == j:
                        # Correlación consigo mismo = 1.0
                        corr = 1.0
                    else:
                        # Calcular correlación
                        series_a, series_b, dates = get_aligned_returns(ticker_a, ticker_b)
                        
                        if len(series_a) < 2:
                            print(f"  ⚠️  {ticker_a} vs {ticker_b}: Datos insuficientes")
                            corr = 0.0
                        else:
                            corr = pearson_correlation(series_a, series_b)
                    
                    # Guardar en DB (ticker_a, ticker_b)
                    cursor.execute("""
                        INSERT INTO correlation_cache (ticker_a, ticker_b, correlation)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (ticker_a, ticker_b) 
                        DO UPDATE SET 
                            correlation = EXCLUDED.correlation,
                            calculated_at = NOW();
                    """, (ticker_a, ticker_b, corr))
                    
                    # Guardar también la inversa (ticker_b, ticker_a) si no es diagonal
                    if i != j:
                        cursor.execute("""
                            INSERT INTO correlation_cache (ticker_a, ticker_b, correlation)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (ticker_a, ticker_b) 
                            DO UPDATE SET 
                                correlation = EXCLUDED.correlation,
                                calculated_at = NOW();
                        """, (ticker_b, ticker_a, corr))
                    
                    total_correlations += 1
                    successful += 1
                    
                    # Mostrar progreso cada 10 correlaciones
                    if total_correlations % 10 == 0:
                        print(f"  ✓ Procesadas: {total_correlations}/{len(tickers) * (len(tickers) + 1) // 2}")
                    
                except Exception as e:
                    failed += 1
                    print(f"  ❌ Error {ticker_a} vs {ticker_b}: {str(e)[:50]}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    elapsed = time.time() - start_time
    
    print(f"\n✅ Matriz de correlación guardada")
    print(f"   • Exitosas: {successful}")
    print(f"   • Fallidas: {failed}")
    print(f"   • Tiempo: {elapsed:.2f} segundos")
    
    return successful, failed


def save_all_volatility():
    """
    Calcula y guarda la volatilidad de todos los activos.
    
    Complejidad: O(n × m) donde n = número de activos, m = longitud de series
    """
    print("\n" + "="*60)
    print("📈 CALCULANDO VOLATILIDAD DE TODOS LOS ACTIVOS")
    print("="*60)
    
    start_time = time.time()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Calcular volatilidad de todos los activos
    volatility_data = get_all_assets_volatility()
    
    print(f"📊 Activos procesados: {len(volatility_data)}")
    
    successful = 0
    failed = 0
    
    for item in volatility_data:
        try:
            cursor.execute("""
                INSERT INTO volatility_cache 
                (ticker, annual_volatility, recent_volatility, risk_level, mean_return, data_points)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (ticker) 
                DO UPDATE SET 
                    annual_volatility = EXCLUDED.annual_volatility,
                    recent_volatility = EXCLUDED.recent_volatility,
                    risk_level = EXCLUDED.risk_level,
                    mean_return = EXCLUDED.mean_return,
                    data_points = EXCLUDED.data_points,
                    calculated_at = NOW();
            """, (
                item['ticker'],
                item['annual_volatility'],
                item['recent_volatility'],
                item['risk_level'],
                item['mean_return'],
                item.get('data_points', 0)  # Agregar si no existe
            ))
            
            successful += 1
            print(f"  ✓ {item['ticker']}: {item['annual_volatility']:.2f}% ({item['risk_level']})")
            
        except Exception as e:
            failed += 1
            print(f"  ❌ Error {item['ticker']}: {str(e)[:50]}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    elapsed = time.time() - start_time
    
    print(f"\n✅ Volatilidad guardada")
    print(f"   • Exitosas: {successful}")
    print(f"   • Fallidas: {failed}")
    print(f"   • Tiempo: {elapsed:.2f} segundos")
    
    return successful, failed


def save_benchmark_results():
    """
    Ejecuta y guarda el benchmark de ordenamiento.
    
    Complejidad: Depende de cada algoritmo (O(n log n) a O(n²))
    """
    print("\n" + "="*60)
    print("⚡ EJECUTANDO BENCHMARK DE ORDENAMIENTO")
    print("="*60)
    
    start_time = time.time()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Ejecutar benchmark
    print("🔄 Ejecutando 12 algoritmos de ordenamiento...")
    print("   (Esto puede tardar 10-30 segundos)")
    
    results = run_benchmark()
    
    print(f"\n📊 Algoritmos ejecutados: {len(results)}")
    
    # Mapeo de complejidades
    complexity_map = {
        'TimSort': 'O(n log n)',
        'QuickSort': 'O(n log n)',
        'HeapSort': 'O(n log n)',
        'Tree Sort': 'O(n log n)',
        'Bitonic Sort': 'O(n log²n)',
        'RadixSort': 'O(nk)',
        'Bucket Sort': 'O(n + k)',
        'Pigeonhole Sort': 'O(n + Rango)',
        'Comb Sort': 'O(n² / 2^p)',
        'Selection Sort': 'O(n²)',
        'Gnome Sort': 'O(n²)',
        'Binary Insertion Sort': 'O(n²)'
    }
    
    successful = 0
    failed = 0
    
    for result in results:
        try:
            complexity = complexity_map.get(result['algorithm'], 'O(?)')
            
            cursor.execute("""
                INSERT INTO benchmark_cache (algorithm, time_seconds, records, complexity)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (algorithm) 
                DO UPDATE SET 
                    time_seconds = EXCLUDED.time_seconds,
                    records = EXCLUDED.records,
                    complexity = EXCLUDED.complexity,
                    calculated_at = NOW();
            """, (
                result['algorithm'],
                result['time_seconds'],
                result['records'],
                complexity
            ))
            
            successful += 1
            print(f"  ✓ {result['algorithm']:<25} {result['time_seconds']:.4f}s  {complexity}")
            
        except Exception as e:
            failed += 1
            print(f"  ❌ Error {result['algorithm']}: {str(e)[:50]}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    elapsed = time.time() - start_time
    
    print(f"\n✅ Benchmark guardado")
    print(f"   • Exitosos: {successful}")
    print(f"   • Fallidos: {failed}")
    print(f"   • Tiempo: {elapsed:.2f} segundos")
    
    return successful, failed


def precompute_all():
    """
    Ejecuta todos los pre-cálculos en secuencia.
    """
    print("\n" + "="*60)
    print("🚀 INICIANDO PRE-CÁLCULO DE DATOS")
    print("="*60)
    print(f"⏰ Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    total_start = time.time()
    
    # Resumen de resultados
    results = {
        'correlation': {'success': 0, 'failed': 0},
        'volatility': {'success': 0, 'failed': 0},
        'benchmark': {'success': 0, 'failed': 0}
    }
    
    try:
        # 1. Matriz de correlación
        success, failed = save_correlation_matrix()
        results['correlation']['success'] = success
        results['correlation']['failed'] = failed
        
        # 2. Volatilidad
        success, failed = save_all_volatility()
        results['volatility']['success'] = success
        results['volatility']['failed'] = failed
        
        # 3. Benchmark
        success, failed = save_benchmark_results()
        results['benchmark']['success'] = success
        results['benchmark']['failed'] = failed
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        sys.exit(1)
    
    total_elapsed = time.time() - total_start
    
    # Resumen final
    print("\n" + "="*60)
    print("📋 RESUMEN FINAL")
    print("="*60)
    print(f"⏰ Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️  Tiempo total: {total_elapsed:.2f} segundos ({total_elapsed/60:.1f} minutos)")
    print()
    print("Resultados por módulo:")
    print(f"  • Correlación:  {results['correlation']['success']} exitosas, {results['correlation']['failed']} fallidas")
    print(f"  • Volatilidad:  {results['volatility']['success']} exitosas, {results['volatility']['failed']} fallidas")
    print(f"  • Benchmark:    {results['benchmark']['success']} exitosos, {results['benchmark']['failed']} fallidos")
    print()
    
    total_success = sum(r['success'] for r in results.values())
    total_failed = sum(r['failed'] for r in results.values())
    
    if total_failed == 0:
        print("✅ TODOS LOS DATOS PRE-CALCULADOS EXITOSAMENTE")
    else:
        print(f"⚠️  COMPLETADO CON {total_failed} ERRORES")
    
    print("="*60)
    print()
    print("💡 Próximos pasos:")
    print("   1. Verificar los datos en la base de datos")
    print("   2. Reiniciar el servidor backend")
    print("   3. Probar los endpoints optimizados")
    print()


def verify_cache():
    """
    Verifica que los datos estén en la caché.
    """
    print("\n" + "="*60)
    print("🔍 VERIFICANDO DATOS EN CACHÉ")
    print("="*60)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificar correlación
    cursor.execute("SELECT COUNT(*) FROM correlation_cache;")
    corr_count = cursor.fetchone()[0]
    print(f"📊 Correlaciones: {corr_count} registros")
    
    # Verificar volatilidad
    cursor.execute("SELECT COUNT(*) FROM volatility_cache;")
    vol_count = cursor.fetchone()[0]
    print(f"📈 Volatilidad: {vol_count} activos")
    
    # Verificar benchmark
    cursor.execute("SELECT COUNT(*) FROM benchmark_cache;")
    bench_count = cursor.fetchone()[0]
    print(f"⚡ Benchmark: {bench_count} algoritmos")
    
    cursor.close()
    conn.close()
    
    print()
    if corr_count > 0 and vol_count > 0 and bench_count > 0:
        print("✅ Todos los datos están en caché")
    else:
        print("⚠️  Faltan datos en caché. Ejecutar: python -m app.cache.precompute")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        verify_cache()
    else:
        precompute_all()
