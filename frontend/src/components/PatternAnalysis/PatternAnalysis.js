import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './PatternAnalysis.css';

const API_BASE_URL = 'http://localhost:8000';

function PatternAnalysis() {
  const [assets, setAssets] = useState([]);
  const [selectedTicker, setSelectedTicker] = useState('');
  const [patternData, setPatternData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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

  const analyzePatterns = async () => {
    if (!selectedTicker) {
      alert('Por favor selecciona un activo');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get(`${API_BASE_URL}/patterns/${selectedTicker}`);
      setPatternData(response.data);
      setLoading(false);
    } catch (err) {
      setError('Error al analizar los patrones del activo');
      setLoading(false);
    }
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'CONSERVADOR':
        return '#4caf50';
      case 'MODERADO':
        return '#ff9800';
      case 'AGRESIVO':
        return '#f44336';
      default:
        return '#9e9e9e';
    }
  };

  return (
    <div className="pattern-container">
      <div className="card">
        <h2>🎯 Análisis de Patrones</h2>
        <p className="pattern-description">
          Detecta patrones en series temporales usando algoritmos de ventanas deslizantes.
          Analiza días consecutivos al alza y picos de volatilidad.
        </p>

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

        <button 
          className="btn btn-primary" 
          onClick={analyzePatterns}
          disabled={loading || !selectedTicker}
        >
          {loading ? '⏳ Analizando...' : '🎯 Analizar Patrones'}
        </button>

        {error && (
          <div className="error pattern-error">
            {error}
          </div>
        )}
      </div>

      {patternData && (
        <>
          <div className="card">
            <h3>📊 Resumen del Activo: {patternData.ticker}</h3>
            
            <div className="stats-grid">
              <div 
                className="stat-card"
                style={{ 
                  background: `linear-gradient(135deg, ${getRiskColor(patternData.risk_classification)} 0%, ${getRiskColor(patternData.risk_classification)}dd 100%)`
                }}
              >
                <h4>Clasificación de Riesgo</h4>
                <div className="value">{patternData.risk_classification}</div>
                <div className="label">Basado en volatilidad</div>
              </div>

              <div className="stat-card">
                <h4>Volatilidad Anual</h4>
                <div className="value">{patternData.volatility_metrics.annual_volatility}%</div>
                <div className="label">σ_anual = σ_diaria × √252</div>
              </div>

              <div className="stat-card">
                <h4>Retorno Medio Diario</h4>
                <div 
                  className="value" 
                  style={{ 
                    color: patternData.volatility_metrics.mean_return >= 0 ? '#4caf50' : '#f44336'
                  }}
                >
                  {patternData.volatility_metrics.mean_return >= 0 ? '+' : ''}
                  {patternData.volatility_metrics.mean_return}%
                </div>
                <div className="label">Promedio histórico</div>
              </div>

              <div className="stat-card">
                <h4>Puntos de Datos</h4>
                <div className="value">{patternData.volatility_metrics.data_points}</div>
                <div className="label">Días analizados</div>
              </div>
            </div>
          </div>

          <div className="card">
            <h3>📈 Patrón 1: Días Consecutivos al Alza</h3>
            <p className="pattern-section-description">
              Algoritmo de ventana deslizante que detecta secuencias de 3 días consecutivos con precios crecientes.
              <br/>
              <strong>Complejidad:</strong> O(n × w) donde n = longitud de la serie, w = tamaño de ventana
            </p>

            <div className="pattern-metrics-grid">
              <div className="pattern-metric-box pattern-metric-frequency">
                <div className="metric-label">Frecuencia</div>
                <div className="metric-value-large">
                  {patternData.consecutive_rises.frequency}
                </div>
                <div className="metric-unit">ocurrencias</div>
              </div>

              <div className="pattern-metric-box pattern-metric-percentage">
                <div className="metric-label">Porcentaje</div>
                <div className="metric-value-large">
                  {patternData.consecutive_rises.frequency_pct.toFixed(2)}%
                </div>
                <div className="metric-unit">del total</div>
              </div>

              <div className="pattern-metric-box pattern-metric-windows">
                <div className="metric-label">Total Ventanas</div>
                <div className="metric-value-large">
                  {patternData.consecutive_rises.total_windows}
                </div>
                <div className="metric-unit">analizadas</div>
              </div>
            </div>

            {patternData.consecutive_rises.top_occurrences.length > 0 && (
              <>
                <h4 className="pattern-table-title">Top 5 Ocurrencias</h4>
                <div style={{ overflowX: 'auto' }}>
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Fecha Inicio</th>
                        <th>Fecha Fin</th>
                        <th>Precio Inicio</th>
                        <th>Precio Fin</th>
                        <th>Cambio %</th>
                      </tr>
                    </thead>
                    <tbody>
                      {patternData.consecutive_rises.top_occurrences.map((occ, index) => (
                        <tr key={index}>
                          <td>{index + 1}</td>
                          <td>{occ.start_date}</td>
                          <td>{occ.end_date}</td>
                          <td>${occ.start_price.toFixed(2)}</td>
                          <td>${occ.end_price.toFixed(2)}</td>
                          <td className={occ.change_pct >= 0 ? 'change-positive' : 'change-negative'}>
                            {occ.change_pct >= 0 ? '+' : ''}{occ.change_pct.toFixed(2)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            )}
          </div>

          <div className="card">
            <h3>📊 Patrón 2: Picos de Volatilidad</h3>
            <p className="pattern-section-description">
              Detecta ventanas donde la desviación estándar supera 2× la volatilidad global.
              <br/>
              <strong>Fórmula:</strong> σ_ventana &gt; threshold × σ_global
              <br/>
              <strong>Complejidad:</strong> O(n × w)
            </p>

            <div className="pattern-metrics-grid">
              <div className="pattern-metric-box pattern-metric-spikes">
                <div className="metric-label">Picos Detectados</div>
                <div className="metric-value-large">
                  {patternData.volatility_spikes.frequency}
                </div>
                <div className="metric-unit">ocurrencias</div>
              </div>

              <div className="pattern-metric-box pattern-metric-spike-pct">
                <div className="metric-label">Porcentaje</div>
                <div className="metric-value-large">
                  {patternData.volatility_spikes.frequency_pct.toFixed(2)}%
                </div>
                <div className="metric-unit">del total</div>
              </div>

              <div className="pattern-metric-box pattern-metric-global">
                <div className="metric-label">Volatilidad Global</div>
                <div className="metric-value-large">
                  {patternData.volatility_spikes.global_volatility}%
                </div>
                <div className="metric-unit">σ de referencia</div>
              </div>
            </div>

            {patternData.volatility_spikes.top_occurrences.length > 0 && (
              <>
                <h4 className="pattern-table-title">Top 5 Picos de Volatilidad</h4>
                <div style={{ overflowX: 'auto' }}>
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Fecha Inicio</th>
                        <th>Fecha Fin</th>
                        <th>Volatilidad Ventana</th>
                        <th>Volatilidad Global</th>
                        <th>Ratio</th>
                      </tr>
                    </thead>
                    <tbody>
                      {patternData.volatility_spikes.top_occurrences.map((spike, index) => (
                        <tr key={index}>
                          <td>{index + 1}</td>
                          <td>{spike.start_date}</td>
                          <td>{spike.end_date}</td>
                          <td className="spike-volatility">
                            {spike.window_volatility}%
                          </td>
                          <td>{spike.global_volatility}%</td>
                          <td>
                            <span className={`ratio-badge ${spike.ratio >= 3 ? 'ratio-high' : 'ratio-medium'}`}>
                              {spike.ratio}×
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            )}
          </div>

          <div className="card">
            <h3>📚 Interpretación de Patrones</h3>
            <div className="pattern-interpretation">
              <p>
                <strong>Días Consecutivos al Alza ({patternData.consecutive_rises.frequency_pct.toFixed(2)}%):</strong> {
                  patternData.consecutive_rises.frequency_pct > 15 
                    ? 'El activo muestra una tendencia alcista frecuente. Esto puede indicar momentum positivo sostenido.'
                    : patternData.consecutive_rises.frequency_pct > 8
                    ? 'El activo tiene una frecuencia normal de rachas alcistas. Comportamiento típico del mercado.'
                    : 'El activo tiene pocas rachas alcistas consecutivas. Puede indicar alta volatilidad o tendencia lateral.'
                }
              </p>

              <p>
                <strong>Picos de Volatilidad ({patternData.volatility_spikes.frequency_pct.toFixed(2)}%):</strong> {
                  patternData.volatility_spikes.frequency_pct > 5
                    ? 'El activo experimenta picos de volatilidad frecuentes. Mayor riesgo y oportunidades de trading.'
                    : patternData.volatility_spikes.frequency_pct > 2
                    ? 'El activo tiene picos de volatilidad ocasionales. Comportamiento normal del mercado.'
                    : 'El activo es relativamente estable con pocos picos de volatilidad extrema.'
                }
              </p>

              <p>
                <strong>Clasificación de Riesgo ({patternData.risk_classification}):</strong> {
                  patternData.risk_classification === 'CONSERVADOR'
                    ? 'Activo de bajo riesgo, adecuado para inversores conservadores que buscan estabilidad.'
                    : patternData.risk_classification === 'MODERADO'
                    ? 'Activo de riesgo medio, balance entre estabilidad y potencial de crecimiento.'
                    : 'Activo de alto riesgo, mayor potencial de retorno pero también de pérdidas significativas.'
                }
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default PatternAnalysis;
