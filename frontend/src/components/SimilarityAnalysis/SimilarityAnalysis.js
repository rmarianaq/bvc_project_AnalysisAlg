import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './SimilarityAnalysis.css';

const API_BASE_URL = 'http://localhost:8000';

function SimilarityAnalysis() {
  const [assets, setAssets] = useState([]);
  const [tickerA, setTickerA] = useState('');
  const [tickerB, setTickerB] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAssets();
  }, []);

  const fetchAssets = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/assets`);
      setAssets(response.data);
      if (response.data.length >= 2) {
        setTickerA(response.data[0].ticker);
        setTickerB(response.data[1].ticker);
      }
    } catch (err) {
      setError('Error al cargar los activos');
    }
  };

  const compareSimilarity = async () => {
    if (!tickerA || !tickerB) {
      alert('Por favor selecciona ambos activos');
      return;
    }

    if (tickerA === tickerB) {
      alert('Por favor selecciona dos activos diferentes');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.post(`${API_BASE_URL}/similarity/compare`, {
        ticker_a: tickerA,
        ticker_b: tickerB
      });
      
      setResult(response.data);
      setLoading(false);
    } catch (err) {
      setError('Error al calcular la similitud. Verifica que ambos activos tengan datos.');
      setLoading(false);
    }
  };

  const getCorrelationColor = (value) => {
    if (value > 0.7) return '#4caf50';
    if (value > 0.3) return '#ff9800';
    if (value > -0.3) return '#9e9e9e';
    if (value > -0.7) return '#ff5722';
    return '#f44336';
  };

  const getCorrelationLabel = (value) => {
    if (value > 0.7) return 'Fuerte Positiva';
    if (value > 0.3) return 'Moderada Positiva';
    if (value > -0.3) return 'Débil';
    if (value > -0.7) return 'Moderada Negativa';
    return 'Fuerte Negativa';
  };

  return (
    <div className="similarity-container">
      <div className="card">
        <h2>🔍 Análisis de Similitud entre Activos</h2>
        <p className="similarity-description">
          Compara dos activos usando 4 algoritmos diferentes: Distancia Euclidiana, 
          Correlación de Pearson, Similitud por Coseno y Dynamic Time Warping (DTW).
        </p>

        <div className="similarity-form-grid">
          <div className="form-group">
            <label>Activo A</label>
            <select 
              value={tickerA} 
              onChange={(e) => setTickerA(e.target.value)}
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
            <label>Activo B</label>
            <select 
              value={tickerB} 
              onChange={(e) => setTickerB(e.target.value)}
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
        </div>

        <button 
          className="btn btn-primary" 
          onClick={compareSimilarity}
          disabled={loading || !tickerA || !tickerB}
        >
          {loading ? '⏳ Calculando...' : '🔍 Comparar Similitud'}
        </button>

        {error && (
          <div className="error similarity-error">
            {error}
          </div>
        )}
      </div>

      {result && (
        <>
          <div className="card">
            <h3>📊 Información de la Comparación</h3>
            <div className="similarity-info-grid">
              <div className="similarity-info-box">
                <div className="info-label">Activo A</div>
                <div className="info-value">{result.ticker_a}</div>
              </div>
              <div className="similarity-info-box">
                <div className="info-label">Activo B</div>
                <div className="info-value">{result.ticker_b}</div>
              </div>
              <div className="similarity-info-box">
                <div className="info-label">Fechas Comunes</div>
                <div className="info-value">{result.common_dates}</div>
              </div>
              <div className="similarity-info-box">
                <div className="info-label">Período</div>
                <div className="info-value info-value-small">
                  {result.date_from} <br/> {result.date_to}
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <h3>📈 Resultados de Similitud</h3>
            
            <div className="similarity-results-grid">
              <div className="similarity-metric-card euclidean">
                <h4>Distancia Euclidiana</h4>
                <div className="metric-value">
                  {result.euclidean.toFixed(6)}
                </div>
                <div className="metric-complexity">
                  Complejidad: O(n)
                </div>
                <div className="metric-note">
                  Más cercano a 0 = más similar
                </div>
              </div>

              <div 
                className="similarity-metric-card pearson"
                style={{ 
                  background: `linear-gradient(135deg, ${getCorrelationColor(result.pearson)} 0%, ${getCorrelationColor(result.pearson)}dd 100%)`
                }}
              >
                <h4>Correlación de Pearson</h4>
                <div className="metric-value">
                  {result.pearson.toFixed(6)}
                </div>
                <div className="metric-complexity">
                  Complejidad: O(n)
                </div>
                <div className="metric-label">
                  {getCorrelationLabel(result.pearson)}
                </div>
              </div>

              <div className="similarity-metric-card cosine">
                <h4>Similitud por Coseno</h4>
                <div className="metric-value">
                  {result.cosine.toFixed(6)}
                </div>
                <div className="metric-complexity">
                  Complejidad: O(n)
                </div>
                <div className="metric-note">
                  Rango: [-1, 1]
                </div>
              </div>

              <div className="similarity-metric-card dtw">
                <h4>Dynamic Time Warping</h4>
                <div className="metric-value">
                  {result.dtw.toFixed(6)}
                </div>
                <div className="metric-complexity">
                  Complejidad: O(n²)
                </div>
                <div className="metric-note">
                  Permite desfases temporales
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <h3>📚 Interpretación de Resultados</h3>
            <div className="similarity-interpretation">
              <p><strong>Distancia Euclidiana ({result.euclidean.toFixed(4)}):</strong> {
                result.euclidean < 0.1 ? 'Las series son muy similares en magnitud.' :
                result.euclidean < 0.5 ? 'Las series tienen similitud moderada.' :
                'Las series son bastante diferentes en magnitud.'
              }</p>
              
              <p><strong>Correlación de Pearson ({result.pearson.toFixed(4)}):</strong> {
                result.pearson > 0.7 ? 'Correlación positiva fuerte. Los activos tienden a moverse juntos.' :
                result.pearson > 0.3 ? 'Correlación positiva moderada. Hay cierta tendencia a moverse juntos.' :
                result.pearson > -0.3 ? 'Correlación débil. Los movimientos son independientes.' :
                result.pearson > -0.7 ? 'Correlación negativa moderada. Tienden a moverse en direcciones opuestas.' :
                'Correlación negativa fuerte. Se mueven en direcciones opuestas.'
              }</p>
              
              <p><strong>Similitud por Coseno ({result.cosine.toFixed(4)}):</strong> {
                result.cosine > 0.9 ? 'Los vectores de retornos tienen la misma dirección.' :
                result.cosine > 0.5 ? 'Los vectores tienen direcciones similares.' :
                'Los vectores tienen direcciones diferentes.'
              }</p>
              
              <p><strong>DTW ({result.dtw.toFixed(4)}):</strong> Considera desfases temporales. Útil para detectar patrones similares que ocurren en momentos diferentes.</p>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default SimilarityAnalysis;
