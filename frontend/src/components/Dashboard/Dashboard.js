import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Dashboard.css';

const API_BASE_URL = 'http://localhost:8000';

function Dashboard() {
  const [assets, setAssets] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Obtener activos
      const assetsResponse = await axios.get(`${API_BASE_URL}/assets`);
      setAssets(assetsResponse.data);

      // Obtener health check para stats
      const healthResponse = await axios.get(`${API_BASE_URL}/health`);
      setStats(healthResponse.data);

      setLoading(false);
    } catch (err) {
      setError('Error al cargar los datos. Asegúrate de que el backend está corriendo en http://localhost:8000');
      setLoading(false);
    }
  };

  const downloadPDF = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/reports/generate-pdf`, {}, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'reporte_tecnico_bvc.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Error al generar el PDF. Esto puede tardar 2-3 minutos.');
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Cargando datos...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="error">
          <h3>⚠️ Error de Conexión</h3>
          <p>{error}</p>
          <button className="btn btn-primary" onClick={fetchDashboardData} style={{ marginTop: '1rem' }}>
            🔄 Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="card">
        <h2>📊 Dashboard Principal</h2>
        
        {stats && (
          <div className="dashboard-stats-grid">
            <div className="dashboard-stat-card">
              <h4>Estado del Sistema</h4>
              <div className="value">{stats.status === 'healthy' ? '✅' : '❌'}</div>
              <div className="label">{stats.status === 'healthy' ? 'Operativo' : 'Error'}</div>
            </div>
            
            <div className="dashboard-stat-card">
              <h4>Base de Datos</h4>
              <div className="value">{stats.database === 'connected' ? '🟢' : '🔴'}</div>
              <div className="label">{stats.database === 'connected' ? 'Conectada' : 'Desconectada'}</div>
            </div>
            
            <div className="dashboard-stat-card">
              <h4>Total de Activos</h4>
              <div className="value">{stats.assets_count}</div>
              <div className="label">Activos registrados</div>
            </div>
            
            <div className="dashboard-stat-card">
              <h4>Reporte PDF</h4>
              <div className="value">📄</div>
              <button 
                className="btn btn-secondary" 
                onClick={downloadPDF}
                style={{ marginTop: '0.5rem', width: '100%' }}
              >
                Descargar
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="card">
        <h2>📈 Portafolio de Activos</h2>
        <p style={{ marginBottom: '1rem', color: '#666' }}>
          Total de {assets.length} activos financieros analizados
        </p>
        
        <div style={{ overflowX: 'auto' }}>
          <table className="dashboard-assets-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Ticker</th>
                <th>Nombre</th>
                <th>Mercado</th>
                <th>Tipo</th>
              </tr>
            </thead>
            <tbody>
              {assets.map((asset, index) => (
                <tr key={asset.id}>
                  <td>{index + 1}</td>
                  <td><strong>{asset.ticker}</strong></td>
                  <td>{asset.name}</td>
                  <td>
                    <span className={`dashboard-market-badge ${asset.market === 'BVC' ? 'bvc' : 'global'}`}>
                      {asset.market}
                    </span>
                  </td>
                  <td>{asset.asset_type}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="card">
        <h2>ℹ️ Información del Proyecto</h2>
        <div className="dashboard-info-section">
          <p><strong>Universidad:</strong> Universidad del Quindío</p>
          <p><strong>Programa:</strong> Ingeniería de Sistemas y Computación</p>
          <p><strong>Materia:</strong> Análisis de Algoritmos</p>
          <p><strong>Proyecto:</strong> Análisis Algorítmico de Activos Financieros BVC</p>
          <p><strong>Año:</strong> 2026</p>
          
          <div className="dashboard-features-box">
            <h3>Funcionalidades Implementadas:</h3>
            <ul>
              <li>✅ ETL automatizado (Extracción, Limpieza, Unificación)</li>
              <li>✅ 4 Algoritmos de similitud (Euclidiana, Pearson, Coseno, DTW)</li>
              <li>✅ Detección de patrones con ventanas deslizantes</li>
              <li>✅ Análisis de volatilidad y clasificación de riesgo</li>
              <li>✅ Matriz de correlación completa</li>
              <li>✅ Generación de reportes en PDF</li>
              <li>✅ 12 Algoritmos de ordenamiento con benchmark</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
