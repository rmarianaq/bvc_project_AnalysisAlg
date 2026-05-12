"""
Script de prueba para verificar que todos los endpoints de la API funcionan correctamente.

Ejecutar después de iniciar el servidor:
    uvicorn app.main:app --reload

Luego en otra terminal:
    python test_api.py
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"


def print_section(title):
    """Imprime un separador visual."""
    print("\n" + "=" * 70)
    print(f"   {title}")
    print("=" * 70)


def test_health():
    """Prueba el endpoint de health check."""
    print_section("TEST 1: Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✅ Health check OK")


def test_get_assets():
    """Prueba el endpoint de obtener activos."""
    print_section("TEST 2: Obtener lista de activos")
    
    response = requests.get(f"{BASE_URL}/assets")
    print(f"Status: {response.status_code}")
    
    assets = response.json()
    print(f"Total de activos: {len(assets)}")
    print(f"Primeros 5 activos:")
    for asset in assets[:5]:
        print(f"  - {asset['ticker']}: {asset['name']} ({asset['market']})")
    
    assert response.status_code == 200
    assert len(assets) > 0
    print("✅ Obtener activos OK")
    
    return assets


def test_get_prices(ticker="ECOPETROL.CL"):
    """Prueba el endpoint de obtener precios."""
    print_section(f"TEST 3: Obtener precios de {ticker}")
    
    response = requests.get(f"{BASE_URL}/assets/{ticker}/prices?limit=10")
    print(f"Status: {response.status_code}")
    
    prices = response.json()
    print(f"Últimos 10 precios de {ticker}:")
    for price in prices[:5]:
        print(f"  {price['date']}: Close=${price['close']:.2f}, Volume={price['volume']:,}")
    
    assert response.status_code == 200
    assert len(prices) > 0
    print("✅ Obtener precios OK")


def test_similarity():
    """Prueba el endpoint de comparación de similitud."""
    print_section("TEST 4: Comparar similitud entre VOO y SPY")
    
    payload = {
        "ticker_a": "VOO",
        "ticker_b": "SPY"
    }
    
    response = requests.post(
        f"{BASE_URL}/similarity/compare",
        json=payload
    )
    print(f"Status: {response.status_code}")
    
    result = response.json()
    print(f"Comparación: {result['ticker_a']} vs {result['ticker_b']}")
    print(f"Fechas comunes: {result['common_dates']}")
    print(f"Período: {result['date_from']} a {result['date_to']}")
    print(f"\nMétricas de similitud:")
    print(f"  - Euclidiana: {result['euclidean']:.6f}")
    print(f"  - Pearson:    {result['pearson']:.6f}")
    print(f"  - Coseno:     {result['cosine']:.6f}")
    print(f"  - DTW:        {result['dtw']:.6f}")
    
    assert response.status_code == 200
    assert result['pearson'] > 0.9  # VOO y SPY deben estar muy correlacionados
    print("✅ Comparación de similitud OK")


def test_correlation_matrix():
    """Prueba el endpoint de matriz de correlación."""
    print_section("TEST 5: Obtener matriz de correlación")
    
    print("⏳ Calculando matriz de correlación (puede tardar 1-2 minutos)...")
    start = time.time()
    
    response = requests.get(f"{BASE_URL}/similarity/correlation-matrix")
    elapsed = time.time() - start
    
    print(f"Status: {response.status_code}")
    print(f"Tiempo de cálculo: {elapsed:.2f} segundos")
    
    result = response.json()
    print(f"Activos en la matriz: {len(result['tickers'])}")
    print(f"Dimensiones de la matriz: {len(result['matrix'])}x{len(result['matrix'][0])}")
    
    # Mostrar algunas correlaciones interesantes
    tickers = result['tickers']
    matrix = result['matrix']
    
    print("\nAlgunas correlaciones destacadas:")
    voo_idx = tickers.index("VOO") if "VOO" in tickers else 0
    spy_idx = tickers.index("SPY") if "SPY" in tickers else 1
    
    print(f"  VOO vs SPY: {matrix[voo_idx][spy_idx]:.4f}")
    
    assert response.status_code == 200
    assert len(result['tickers']) > 0
    print("✅ Matriz de correlación OK")


def test_patterns(ticker="ECOPETROL.CL"):
    """Prueba el endpoint de análisis de patrones."""
    print_section(f"TEST 6: Análisis de patrones de {ticker}")
    
    response = requests.get(f"{BASE_URL}/patterns/{ticker}")
    print(f"Status: {response.status_code}")
    
    result = response.json()
    print(f"Análisis de patrones para {result['ticker']}:")
    print(f"\n📈 Patrón 1: Días consecutivos al alza")
    print(f"  Frecuencia: {result['consecutive_rises']['frequency']} ocurrencias")
    print(f"  Porcentaje: {result['consecutive_rises']['frequency_pct']:.2f}%")
    
    print(f"\n📊 Patrón 2: Picos de volatilidad")
    print(f"  Frecuencia: {result['volatility_spikes']['frequency']} ocurrencias")
    print(f"  Porcentaje: {result['volatility_spikes']['frequency_pct']:.2f}%")
    
    print(f"\n💹 Volatilidad:")
    print(f"  Anual: {result['volatility_metrics']['annual_volatility']:.2f}%")
    print(f"  Clasificación: {result['risk_classification']}")
    
    assert response.status_code == 200
    assert 'consecutive_rises' in result
    print("✅ Análisis de patrones OK")


def test_volatility_all():
    """Prueba el endpoint de clasificación de riesgo."""
    print_section("TEST 7: Clasificación de riesgo de todos los activos")
    
    response = requests.get(f"{BASE_URL}/volatility/all")
    print(f"Status: {response.status_code}")
    
    results = response.json()
    print(f"Total de activos analizados: {len(results)}")
    print(f"\nTop 10 activos por volatilidad:")
    print(f"{'#':<4} {'Ticker':<18} {'Volatilidad':<14} {'Clasificación'}")
    print("-" * 60)
    
    for i, asset in enumerate(results[:10], 1):
        print(
            f"{i:<4} {asset['ticker']:<18} "
            f"{asset['annual_volatility']:>6.2f}% {'':<6} "
            f"{asset['risk_level']}"
        )
    
    # Contar por clasificación
    conservador = sum(1 for a in results if a['risk_level'] == 'CONSERVADOR')
    moderado = sum(1 for a in results if a['risk_level'] == 'MODERADO')
    agresivo = sum(1 for a in results if a['risk_level'] == 'AGRESIVO')
    
    print(f"\nDistribución por riesgo:")
    print(f"  Conservador: {conservador}")
    print(f"  Moderado:    {moderado}")
    print(f"  Agresivo:    {agresivo}")
    
    assert response.status_code == 200
    assert len(results) > 0
    print("✅ Clasificación de riesgo OK")


def test_candlestick(ticker="VOO"):
    """Prueba el endpoint de datos para candlestick."""
    print_section(f"TEST 8: Datos para gráfico de velas de {ticker}")
    
    response = requests.get(f"{BASE_URL}/candlestick/{ticker}?days=30")
    print(f"Status: {response.status_code}")
    
    data = response.json()
    print(f"Datos obtenidos: {len(data)} días")
    print(f"\nÚltimos 5 días con medias móviles:")
    print(f"{'Fecha':<12} {'Close':<10} {'SMA-20':<10} {'SMA-50':<10}")
    print("-" * 50)
    
    for day in data[-5:]:
        sma20 = f"{day['sma_20']:.2f}" if day['sma_20'] else "N/A"
        sma50 = f"{day['sma_50']:.2f}" if day['sma_50'] else "N/A"
        print(f"{day['date']:<12} ${day['close']:<9.2f} ${sma20:<9} ${sma50:<9}")
    
    assert response.status_code == 200
    assert len(data) > 0
    print("✅ Datos de candlestick OK")


def test_generate_pdf():
    """Prueba el endpoint de generación de PDF."""
    print_section("TEST 9: Generar reporte PDF")
    
    print("⏳ Generando reporte PDF (puede tardar 2-3 minutos)...")
    start = time.time()
    
    response = requests.post(f"{BASE_URL}/reports/generate-pdf")
    elapsed = time.time() - start
    
    print(f"Status: {response.status_code}")
    print(f"Tiempo de generación: {elapsed:.2f} segundos")
    
    if response.status_code == 200:
        # Guardar el PDF
        with open("reporte_test.pdf", "wb") as f:
            f.write(response.content)
        print("✅ PDF generado y guardado como 'reporte_test.pdf'")
    else:
        print(f"❌ Error al generar PDF: {response.text}")
        print("Nota: Asegúrate de tener instalado: pip install reportlab matplotlib seaborn")


def run_all_tests():
    """Ejecuta todos los tests."""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "SUITE DE PRUEBAS - BVC ANALYSIS API" + " " * 18 + "║")
    print("╚" + "═" * 68 + "╝")
    
    try:
        test_health()
        assets = test_get_assets()
        test_get_prices()
        test_similarity()
        test_correlation_matrix()
        test_patterns()
        test_volatility_all()
        test_candlestick()
        test_generate_pdf()
        
        print("\n" + "╔" + "═" * 68 + "╗")
        print("║" + " " * 20 + "✅ TODOS LOS TESTS PASARON" + " " * 21 + "║")
        print("╚" + "═" * 68 + "╝\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: No se pudo conectar al servidor.")
        print("Asegúrate de que el servidor esté corriendo:")
        print("    uvicorn app.main:app --reload")
    except AssertionError as e:
        print(f"\n❌ Test falló: {e}")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")


if __name__ == "__main__":
    run_all_tests()
