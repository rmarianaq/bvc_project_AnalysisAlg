import requests
import time
from datetime import datetime
from app.core.database import get_connection

# ─────────────────────────────────────────────
# PORTAFOLIO DE 22 ACTIVOS
# ─────────────────────────────────────────────
ASSETS = [
    # Acciones colombianas (BVC) - sufijo .CL para Yahoo Finance
    {"ticker": "ECOPETROL.CL", "name": "Ecopetrol S.A.",          "market": "BVC",    "type": "STOCK"},
    {"ticker": "ISA.CL",       "name": "Interconexion Electrica",  "market": "BVC",    "type": "STOCK"},
    {"ticker": "GEB.CL",       "name": "Grupo Energia Bogota",     "market": "BVC",    "type": "STOCK"},
    # {"ticker": "CIB",          "name": "Bancolombia Pref. ADR",    "market": "BVC",    "type": "STOCK"},
    #{"ticker": "NUTRESA.CL",   "name": "Grupo Nutresa",            "market": "BVC",    "type": "STOCK"},
    # {"ticker": "GRUPOSURA.CL", "name": "Grupo Sura",               "market": "BVC",    "type": "STOCK"},
    #{"ticker": "CELSIA.CL",    "name": "Celsia S.A.",              "market": "BVC",    "type": "STOCK"},
    #{"ticker": "BOGOTA.CL",    "name": "Banco de Bogota",          "market": "BVC",    "type": "STOCK"},
    #{"ticker": "EXITO.CL",     "name": "Grupo Exito",              "market": "BVC",    "type": "STOCK"},
    #{"ticker": "CEMARGOS.CL",  "name": "Cementos Argos",           "market": "BVC",    "type": "STOCK"},
    # ETFs y activos globales
    {"ticker": "VOO",          "name": "Vanguard S&P 500 ETF",     "market": "GLOBAL", "type": "ETF"},
    {"ticker": "QQQ",          "name": "Invesco Nasdaq 100",        "market": "GLOBAL", "type": "ETF"},
    #{"ticker": "GLD",          "name": "SPDR Gold Trust",           "market": "GLOBAL", "type": "ETF"},
    #{"ticker": "TLT",          "name": "iShares 20Y Treasury",      "market": "GLOBAL", "type": "ETF"},
    # {"ticker": "VWO",          "name": "Vanguard Emerging Markets", "market": "GLOBAL", "type": "ETF"},
    #{"ticker": "XLF",          "name": "Financial Select Sector",   "market": "GLOBAL", "type": "ETF"},
    #{"ticker": "XLE",          "name": "Energy Select Sector",      "market": "GLOBAL", "type": "ETF"},
    #{"ticker": "ARKK",         "name": "ARK Innovation ETF",        "market": "GLOBAL", "type": "ETF"},
    {"ticker": "BTC-USD",      "name": "Bitcoin USD",               "market": "GLOBAL", "type": "ETF"},
    #{"ticker": "SPY",          "name": "S&P 500 SPDR",              "market": "GLOBAL", "type": "ETF"},
    #{"ticker": "EEM",          "name": "iShares MSCI Emerging",     "market": "GLOBAL", "type": "ETF"},
    #{"ticker": "CSPX.L",       "name": "iShares Core S&P 500",      "market": "GLOBAL", "type": "ETF"},
]

# Headers para simular un navegador real y evitar bloqueos
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def build_url(ticker: str) -> str:
    """
    Construye la URL de la API de Yahoo Finance manualmente.
    - interval=1d  → datos diarios
    - range=5y     → últimos 5 años
    """
    base = "https://query1.finance.yahoo.com/v8/finance/chart/"
    return f"{base}{ticker}?interval=1d&range=5y"


def fetch_ticker_data(ticker: str) -> dict:
    """
    Hace la petición HTTP a Yahoo Finance y retorna el JSON parseado.
    Maneja errores de red, timeouts y respuestas inválidas.
    """
    url = build_url(ticker)
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)

        # Si el servidor retorna error HTTP (404, 500, etc.)
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}"
            }

        data = response.json()

        # Verificar que la respuesta tenga la estructura esperada
        result = data.get("chart", {}).get("result")
        if not result:
            return {
                "success": False,
                "error": "Respuesta vacía o ticker no encontrado"
            }

        return {"success": True, "data": result[0]}

    except requests.exceptions.Timeout:
        return {"success": False, "error": "Timeout - servidor tardó más de 15s"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Sin conexión a internet"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def parse_prices(raw_data: dict) -> list:
    """
    Convierte el JSON crudo de Yahoo Finance en una lista
    de diccionarios con los campos que necesitamos.

    Yahoo Finance retorna los timestamps en formato UNIX
    (segundos desde 1970), los convertimos a fecha legible.
    """
    timestamps = raw_data.get("timestamp", [])
    indicators  = raw_data.get("indicators", {})
    quotes      = indicators.get("quote", [{}])[0]

    opens   = quotes.get("open",   [])
    highs   = quotes.get("high",   [])
    lows    = quotes.get("low",    [])
    closes  = quotes.get("close",  [])
    volumes = quotes.get("volume", [])

    prices = []
    for i in range(len(timestamps)):
        # Saltamos filas donde algún valor es None
        if None in (opens[i], highs[i], lows[i], closes[i], volumes[i]):
            continue

        prices.append({
            "date":   datetime.utcfromtimestamp(timestamps[i]).strftime("%Y-%m-%d"),
            "open":   round(float(opens[i]),   6),
            "high":   round(float(highs[i]),   6),
            "low":    round(float(lows[i]),    6),
            "close":  round(float(closes[i]),  6),
            "volume": int(volumes[i])
        })

    return prices


def save_asset(ticker: str, name: str, market: str, asset_type: str) -> int:
    """
    Guarda o recupera el activo en la tabla assets.
    Si ya existe, retorna su id. Si no, lo inserta.
    Retorna el id del activo.
    """
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO assets (ticker, name, market, asset_type)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name
        RETURNING id;
    """, (ticker, name, market, asset_type))

    asset_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return asset_id


def save_prices(asset_id: int, prices: list) -> int:
    """
    Guarda los precios diarios en la tabla daily_prices.
    Usa ON CONFLICT para no duplicar registros si se ejecuta
    el ETL más de una vez.
    Retorna cuántos registros se insertaron.
    """
    conn    = get_connection()
    cursor  = conn.cursor()
    saved   = 0

    for price in prices:
        cursor.execute("""
            INSERT INTO daily_prices
                (asset_id, trade_date, open_price, high_price,
                 low_price, close_price, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (asset_id, trade_date) DO NOTHING;
        """, (
            asset_id,
            price["date"],
            price["open"],
            price["high"],
            price["low"],
            price["close"],
            price["volume"]
        ))
        saved += cursor.rowcount

    conn.commit()
    cursor.close()
    conn.close()
    return saved


def save_log(ticker: str, status: str, records: int, message: str):
    """
    Registra el resultado de cada descarga en etl_log.
    """
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO etl_log (ticker, status, records, message)
        VALUES (%s, %s, %s, %s);
    """, (ticker, status, records, message))
    conn.commit()
    cursor.close()
    conn.close()


def run_etl():
    """
    Función principal del ETL.
    Recorre todos los activos, descarga, parsea y guarda.
    """
    print("=" * 55)
    print("   INICIANDO ETL - DESCARGA DE DATOS FINANCIEROS")
    print("=" * 55)

    total_ok    = 0
    total_error = 0

    for asset in ASSETS:
        ticker = asset["ticker"]
        print(f"\n📥 Descargando {ticker}...", end=" ")

        # 1. Petición HTTP a Yahoo Finance
        result = fetch_ticker_data(ticker)

        if not result["success"]:
            print(f"❌ Error: {result['error']}")
            save_log(ticker, "ERROR", 0, result["error"])
            total_error += 1
            continue

        # 2. Parsear el JSON a lista de precios
        prices = parse_prices(result["data"])

        if not prices:
            print("⚠️  Sin datos")
            save_log(ticker, "PARTIAL", 0, "Sin precios disponibles")
            total_error += 1
            continue

        # 3. Guardar activo en tabla assets
        asset_id = save_asset(
            ticker,
            asset["name"],
            asset["market"],
            asset["type"]
        )

        # 4. Guardar precios en tabla daily_prices
        saved = save_prices(asset_id, prices)

        print(f"✅ {saved} registros guardados")
        save_log(ticker, "SUCCESS", saved, "Descarga exitosa")
        total_ok += 1

        # Pausa de 1 segundo entre peticiones para no saturar la API
        time.sleep(1)

    print("\n" + "=" * 55)
    print(f"   ETL COMPLETADO: {total_ok} exitosos, {total_error} errores")
    print("=" * 55)


if __name__ == "__main__":
    run_etl()