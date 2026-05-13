import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './VolatilityAnalysis.css';
import { API_BASE_URL } from '../../config';

function VolatilityAnalysis() {
  const [volatilityData, setVolatilityData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('ALL');

  useEffect(() => {
    fetchVolatilityData();
  }, []);

  const fetchVolatilityData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get(`${API_BASE_URL}/volatility/all`);
      setVolatilityData(response.data);
      setLoading(false);
    } catch (err) {
      setError('Error al cargar los datos de volatilidad');
      setLoading(false);
    }
  };

  const getRiskBadgeClass = (riskLevel) => {
    switch (riskLevel) {
      case 'CONSERVADOR':
        return 'risk-conservador';
      case 'MODERADO':
        return 'risk-moderado';
      case 'AGRESIVO':
        return 'risk-agresivo';
      default:
        return '';
    }
  };

  const getRiskIcon = (riskLevel) => {
    switch (riskLevel) {
      case 'CONSERVADOR':
        return '●';
      case 'MODERADO':
        return '●';
      case 'AGRESIVO':
        return '●';
      default:
        return '●';
    }
  };

  const filteredData = filter === 'ALL' 
    ? volatilityData 
    : volatilityData.filter(item => item.risk_level === filter);

  const stats = {
    total: volatilityData.length,
    conservador: volatilityData.filter(item => item.risk_level === 'CONSERVADOR').length,
    moderado: volatilityData.filter(item => item.risk_level === 'MODERADO').length,
    agresivo: volatilityData.filter(item => item.risk_level === 'AGRESIVO').length,
    avgVolatility: volatilityData.length > 0 
      ? (volatilityData.reduce((sum, item) => sum + item.annual_volatility, 0) / volatilityData.length).toFixed(2)
      : 0
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Calculando volatilidad de todos los activos...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="volatility-container">
      <div className="card">
        <h2>Análisis de Volatilidad y Clasificación de Riesgo</h2>
        <p className="volatility-description">
          La volatilidad histórica anualizada se calcula como σ_anual = σ_diaria × √252.
          Los activos se clasifican en tres categorías de riesgo según su volatilidad.
        </p>

        <div className="stats-grid">
          <div className="stat-card volatility-stat-total">
            <h4>Total de Activos</h4>
            <div className="value">{stats.total}</div>
            <div className="label">Analizados</div>
          </div>

          <div className="stat-card volatility-stat-conservador">
            <h4>Conservadores</h4>
            <div className="value">{stats.conservador}</div>
            <div className="label">Volatilidad &lt; 15%</div>
          </div>

          <div className="stat-card volatility-stat-moderado">
            <h4>Moderados</h4>
            <div className="value">{stats.moderado}</div>
            <div className="label">15% ≤ Volatilidad &lt; 25%</div>
          </div>

          <div className="stat-card volatility-stat-agresivo">
            <h4>Agresivos</h4>
            <div className="value">{stats.agresivo}</div>
            <div className="label">Volatilidad ≥ 25%</div>
          </div>
        </div>
      </div>

      <div className="card">
        <h3>Filtrar por Nivel de Riesgo</h3>
        <div className="volatility-filter-buttons">
          <button 
            className={filter === 'ALL' ? 'btn btn-primary' : 'btn btn-secondary'}
            onClick={() => setFilter('ALL')}
          >
            Todos ({stats.total})
          </button>
          <button 
            className={filter === 'CONSERVADOR' ? 'btn btn-primary' : 'btn btn-secondary'}
            onClick={() => setFilter('CONSERVADOR')}
          >
            Conservadores ({stats.conservador})
          </button>
          <button 
            className={filter === 'MODERADO' ? 'btn btn-primary' : 'btn btn-secondary'}
            onClick={() => setFilter('MODERADO')}
          >
            Moderados ({stats.moderado})
          </button>
          <button 
            className={filter === 'AGRESIVO' ? 'btn btn-primary' : 'btn btn-secondary'}
            onClick={() => setFilter('AGRESIVO')}
          >
            Agresivos ({stats.agresivo})
          </button>
        </div>
      </div>

      <div className="card">
        <h3>Clasificación de Activos por Volatilidad</h3>
        <p className="volatility-table-subtitle">
          Mostrando {filteredData.length} de {stats.total} activos
        </p>

        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Ticker</th>
                <th>Volatilidad Anual</th>
                <th>Volatilidad Reciente</th>
                <th>Retorno Medio</th>
                <th>Clasificación</th>
              </tr>
            </thead>
            <tbody>
              {filteredData.map((item, index) => (
                <tr key={item.ticker}>
                  <td>{index + 1}</td>
                  <td><strong>{item.ticker}</strong></td>
                  <td>
                    <div className="volatility-bar-container">
                      <div className="volatility-bar-bg">
                        <div 
                          className={`volatility-bar-fill ${getRiskBadgeClass(item.risk_level)}`}
                          style={{ width: `${Math.min(item.annual_volatility, 100)}%` }}
                        ></div>
                      </div>
                      <span className="volatility-value">{item.annual_volatility.toFixed(2)}%</span>
                    </div>
                  </td>
                  <td>{item.recent_volatility.toFixed(2)}%</td>
                  <td className={item.mean_return >= 0 ? 'return-positive' : 'return-negative'}>
                    {item.mean_return >= 0 ? '+' : ''}{item.mean_return.toFixed(4)}%
                  </td>
                  <td>
                    <span className={`risk-badge ${getRiskBadgeClass(item.risk_level)}`}>
                      {getRiskIcon(item.risk_level)} {item.risk_level}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="card">
        <h3>Criterios de Clasificación</h3>
        <div className="volatility-criteria">
          <div className="criteria-box criteria-conservador">
            <strong>CONSERVADOR (Volatilidad &lt; 15%)</strong>
            <p>
              Activos de bajo riesgo. Típicamente bonos del tesoro, ETFs de renta fija o acciones de empresas muy estables.
              Movimientos de precio predecibles y menor potencial de pérdidas.
            </p>
          </div>

          <div className="criteria-box criteria-moderado">
            <strong>MODERADO (15% ≤ Volatilidad &lt; 25%)</strong>
            <p>
              Activos de riesgo medio. Acciones de mercados desarrollados, ETFs diversificados.
              Balance entre riesgo y retorno potencial.
            </p>
          </div>

          <div className="criteria-box criteria-agresivo">
            <strong>AGRESIVO (Volatilidad ≥ 25%)</strong>
            <p>
              Activos de alto riesgo. Acciones de mercados emergentes, criptomonedas, ETFs sectoriales.
              Mayor potencial de retorno pero también de pérdidas significativas.
            </p>
          </div>
        </div>
      </div>

      <div className="card">
        <h3>Fórmula de Cálculo</h3>
        <div className="volatility-formula">
          <p><strong>Volatilidad Anualizada:</strong></p>
          <p className="formula-text">
            σ_anual = σ_diaria × √252
          </p>
          <p className="formula-description">
            Donde:<br/>
            • σ_diaria = desviación estándar de los retornos diarios<br/>
            • 252 = número aproximado de días de negociación al año<br/>
            • Complejidad algorítmica: O(n)
          </p>
        </div>
      </div>
    </div>
  );
}

export default VolatilityAnalysis;
