import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './CandlestickChart.css';

const API_BASE_URL = 'http://localhost:8000';

function CandlestickChart() {
  const [assets, setAssets] = useState([]);
  const [selectedTicker, setSelectedTicker] = useState('');
  const [candlestickData, setCandlestickData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [days, setDays] = useState(90);

  useEffect(() => {
    fetchAssets();
  }, []);

  const fetchAssets = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/assets`);
      setAssets(response.data);
      if (response.data.length > 0) {
        setSelectedTicker(response.data[0].ticker);
      }
    } catch (err) {
      setError('Error al cargar los activos');
    }
  };

  const fetchCandlestickData = async () => {
    if (!selectedTicker) {
      alert('Por favor selecciona un activo');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get(`${API_BASE_URL}/candlestick/${selectedTicker}?days=${days}`);
      setCandlestickData(response.data);
      setLoading(false);
    } catch (err) {
      setError('Error al cargar los datos del gráfico');
      setLoading(false);
    }
  };

  const renderSimplifiedChart = () => {
    if (!candlestickData || candlestickData.length === 0) return null;

    // Encontrar valores mín y máx para escalar
    const prices = candlestickData.map(d => [d.low, d.high, d.sma_20, d.sma_50]).flat().filter(v => v !== null);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const priceRange = maxPrice - minPrice;

    const chartWidth = 800;
    const chartHeight = 400;
    const padding = 40;
    const candleWidth = Math.max(2, (chartWidth - 2 * padding) / candlestickData.length - 2);

    return (
      <svg width={chartWidth} height={chartHeight + 100} className="candlestick-svg">
        {/* Título */}
        <text x={chartWidth / 2} y={20} textAnchor="middle" className="chart-title">
          Gráfico de Velas con Medias Móviles - {selectedTicker}
        </text>

        {/* Líneas de grid */}
        {[0, 0.25, 0.5, 0.75, 1].map((ratio, i) => {
          const y = padding + chartHeight * (1 - ratio);
          const price = minPrice + priceRange * ratio;
          return (
            <g key={i}>
              <line
                x1={padding}
                y1={y}
                x2={chartWidth - padding}
                y2={y}
                stroke="#e0e0e0"
                strokeWidth="1"
              />
              <text x={padding - 10} y={y + 5} textAnchor="end" fontSize="10" fill="#666">
                ${price.toFixed(2)}
              </text>
            </g>
          );
        })}

        {/* Velas */}
        {candlestickData.map((candle, index) => {
          const x = padding + (index * (chartWidth - 2 * padding)) / candlestickData.length;
          
          const yHigh = padding + chartHeight * (1 - (candle.high - minPrice) / priceRange);
          const yLow = padding + chartHeight * (1 - (candle.low - minPrice) / priceRange);
          const yOpen = padding + chartHeight * (1 - (candle.open - minPrice) / priceRange);
          const yClose = padding + chartHeight * (1 - (candle.close - minPrice) / priceRange);

          const isGreen = candle.close >= candle.open;
          const color = isGreen ? '#4caf50' : '#f44336';
          const bodyTop = Math.min(yOpen, yClose);
          const bodyHeight = Math.abs(yClose - yOpen) || 1;

          return (
            <g key={index}>
              {/* Mecha (high-low) */}
              <line
                x1={x + candleWidth / 2}
                y1={yHigh}
                x2={x + candleWidth / 2}
                y2={yLow}
                stroke={color}
                strokeWidth="1"
              />
              {/* Cuerpo (open-close) */}
              <rect
                x={x}
                y={bodyTop}
                width={candleWidth}
                height={bodyHeight}
                fill={color}
                stroke={color}
              />
            </g>
          );
        })}

        {/* SMA 20 */}
        <polyline
          points={candlestickData
            .map((candle, index) => {
              if (candle.sma_20 === null) return null;
              const x = padding + (index * (chartWidth - 2 * padding)) / candlestickData.length + candleWidth / 2;
              const y = padding + chartHeight * (1 - (candle.sma_20 - minPrice) / priceRange);
              return `${x},${y}`;
            })
            .filter(p => p !== null)
            .join(' ')}
          fill="none"
          stroke="#2196f3"
          strokeWidth="2"
        />

        {/* SMA 50 */}
        <polyline
          points={candlestickData
            .map((candle, index) => {
              if (candle.sma_50 === null) return null;
              const x = padding + (index * (chartWidth - 2 * padding)) / candlestickData.length + candleWidth / 2;
              const y = padding + chartHeight * (1 - (candle.sma_50 - minPrice) / priceRange);
              return `${x},${y}`;
            })
            .filter(p => p !== null)
            .join(' ')}
          fill="none"
          stroke="#ff9800"
          strokeWidth="2"
        />

        {/* Leyenda */}
        <g transform={`translate(${padding}, ${chartHeight + padding + 20})`}>
          <rect x="0" y="0" width="15" height="15" fill="#4caf50" />
          <text x="20" y="12" fontSize="12">Alcista (Close ≥ Open)</text>

          <rect x="150" y="0" width="15" height="15" fill="#f44336" />
          <text x="170" y="12" fontSize="12">Bajista (Close &lt; Open)</text>

          <line x1="300" y1="7" x2="330" y2="7" stroke="#2196f3" strokeWidth="3" />
          <text x="335" y="12" fontSize="12">SMA 20 días</text>

          <line x1="450" y1="7" x2="480" y2="7" stroke="#ff9800" strokeWidth="3" />
          <text x="485" y="12" fontSize="12">SMA 50 días</text>
        </g>

        {/* Etiquetas de fechas (cada 10 velas) */}
        {candlestickData.filter((_, i) => i % Math.floor(candlestickData.length / 6) === 0).map((candle, i, arr) => {
          const index = candlestickData.indexOf(candle);
          const x = padding + (index * (chartWidth - 2 * padding)) / candlestickData.length;
          return (
            <text
              key={index}
              x={x}
              y={chartHeight + padding + 15}
              fontSize="10"
              fill="#666"
              textAnchor="middle"
            >
              {candle.date.substring(5)}
            </text>
          );
        })}
      </svg>
    );
  };

  return (
    <div className="candlestick-container">
      <div className="card">
        <h2>Gráfico de Velas (Candlestick) con Medias Móviles</h2>
        <p className="candlestick-description">
          Visualización de precios OHLC (Open, High, Low, Close) con medias móviles simples (SMA) de 20 y 50 días.
          Las velas verdes indican días alcistas y las rojas días bajistas.
        </p>

        <div className="candlestick-controls">
          <div className="form-group">
            <label>Seleccionar Activo</label>
            <select 
              value={selectedTicker} 
              onChange={(e) => setSelectedTicker(e.target.value)}
              disabled={loading}
            >
              <option value="">Seleccionar...</option>
              {assets.map(asset => (
                <option key={asset.id} value={asset.ticker}>
                  {asset.ticker} - {asset.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Período (días)</label>
            <select 
              value={days} 
              onChange={(e) => setDays(parseInt(e.target.value))}
              disabled={loading}
            >
              <option value="30">30 días</option>
              <option value="60">60 días</option>
              <option value="90">90 días</option>
              <option value="180">180 días</option>
              <option value="365">1 año</option>
            </select>
          </div>

          <button 
            className="btn btn-primary" 
            onClick={fetchCandlestickData}
            disabled={loading || !selectedTicker}
          >
            {loading ? 'Cargando...' : 'Generar Gráfico'}
          </button>
        </div>

        {error && (
          <div className="error candlestick-error">
            {error}
          </div>
        )}
      </div>

      {candlestickData && candlestickData.length > 0 && (
        <>
          <div className="card">
            <h3>Gráfico de Velas</h3>
            <div className="chart-wrapper">
              {renderSimplifiedChart()}
            </div>
          </div>

          <div className="card">
            <h3>Interpretación del Gráfico</h3>
            <div className="candlestick-interpretation">
              <p><strong>Velas (Candlesticks):</strong></p>
              <ul>
                <li><strong>Vela Verde:</strong> El precio de cierre fue mayor que el de apertura (día alcista)</li>
                <li><strong>Vela Roja:</strong> El precio de cierre fue menor que el de apertura (día bajista)</li>
                <li><strong>Mechas:</strong> Representan los precios máximo y mínimo del día</li>
                <li><strong>Cuerpo:</strong> Representa el rango entre apertura y cierre</li>
              </ul>

              <p><strong>Medias Móviles Simples (SMA):</strong></p>
              <ul>
                <li><strong>SMA 20 (azul):</strong> Promedio de los últimos 20 días de cierre. Indica tendencia a corto plazo</li>
                <li><strong>SMA 50 (naranja):</strong> Promedio de los últimos 50 días de cierre. Indica tendencia a mediano plazo</li>
                <li><strong>Cruce alcista:</strong> Cuando SMA 20 cruza por encima de SMA 50, señal de compra</li>
                <li><strong>Cruce bajista:</strong> Cuando SMA 20 cruza por debajo de SMA 50, señal de venta</li>
              </ul>

              <p><strong>Complejidad Algorítmica:</strong></p>
              <p>
                El cálculo de las medias móviles usa un algoritmo de ventana deslizante con complejidad O(n × w),
                donde n es el número de días y w es el tamaño de la ventana (20 o 50 días).
              </p>
            </div>
          </div>

          <div className="card">
            <h3>Estadísticas del Período</h3>
            <div className="stats-grid">
              <div className="stat-card">
                <h4>Precio Inicial</h4>
                <div className="value">${candlestickData[0].open.toFixed(2)}</div>
                <div className="label">{candlestickData[0].date}</div>
              </div>

              <div className="stat-card">
                <h4>Precio Final</h4>
                <div className="value">${candlestickData[candlestickData.length - 1].close.toFixed(2)}</div>
                <div className="label">{candlestickData[candlestickData.length - 1].date}</div>
              </div>

              <div className="stat-card">
                <h4>Precio Máximo</h4>
                <div className="value">${Math.max(...candlestickData.map(d => d.high)).toFixed(2)}</div>
                <div className="label">En el período</div>
              </div>

              <div className="stat-card">
                <h4>Precio Mínimo</h4>
                <div className="value">${Math.min(...candlestickData.map(d => d.low)).toFixed(2)}</div>
                <div className="label">En el período</div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default CandlestickChart;
