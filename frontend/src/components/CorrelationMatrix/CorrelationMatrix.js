import React, { useState } from 'react';
import axios from 'axios';
import './CorrelationMatrix.css';

const API_BASE_URL = 'http://localhost:8000';

function CorrelationMatrix() {
  const [matrixData, setMatrixData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedCell, setSelectedCell] = useState(null);

  const fetchCorrelationMatrix = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get(`${API_BASE_URL}/similarity/correlation-matrix`);
      setMatrixData(response.data);
      setLoading(false);
    } catch (err) {
      setError('Error al calcular la matriz de correlación');
      setLoading(false);
    }
  };

  const getCorrelationColor = (value) => {
    if (value >= 0.7) return '#4caf50';
    if (value >= 0.3) return '#8bc34a';
    if (value >= 0) return '#cddc39';
    if (value >= -0.3) return '#ffeb3b';
    if (value >= -0.7) return '#ff9800';
    return '#f44336';
  };

  const getCorrelationLabel = (value) => {
    if (value >= 0.7) return 'Fuerte Positiva';
    if (value >= 0.3) return 'Moderada Positiva';
    if (value >= -0.3) return 'Débil';
    if (value >= -0.7) return 'Moderada Negativa';
    return 'Fuerte Negativa';
  };

  const handleCellClick = (tickerA, tickerB, value) => {
    if (tickerA !== tickerB) {
      setSelectedCell({ tickerA, tickerB, value });
    }
  };

  return (
    <div className="correlation-container">
      <div className="card">
        <h2>Matriz de Correlación de Pearson</h2>
        <p className="correlation-description">
          Muestra las correlaciones entre todos los activos del portafolio.
          La correlación de Pearson mide la relación lineal entre dos series temporales.
        </p>

        {!matrixData && !loading && (
          <button 
            className="btn btn-primary" 
            onClick={fetchCorrelationMatrix}
          >
            Calcular Matriz de Correlación
          </button>
        )}

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>Calculando correlaciones... Esto puede tardar 1-2 minutos</p>
            <p className="loading-detail">
              Calculando {matrixData ? matrixData.tickers.length : 22}² = {matrixData ? matrixData.tickers.length * matrixData.tickers.length : 484} correlaciones
            </p>
          </div>
        )}

        {error && (
          <div className="error">
            {error}
            <button 
              className="btn btn-primary" 
              onClick={fetchCorrelationMatrix}
              style={{ marginTop: '1rem' }}
            >
              Reintentar
            </button>
          </div>
        )}
      </div>

      {matrixData && !loading && (
        <>
          <div className="card">
            <h3>Matriz de Correlación ({matrixData.tickers.length}×{matrixData.tickers.length})</h3>
            <p className="correlation-matrix-subtitle">
              Haz clic en una celda para ver detalles de la correlación
            </p>

            <div className="correlation-matrix-wrapper">
              <table className="correlation-matrix-table">
                <thead className="correlation-matrix-thead">
                  <tr>
                    <th className="correlation-matrix-corner"></th>
                    {matrixData.tickers.map((ticker, index) => (
                      <th key={index} className="correlation-matrix-header-cell">
                        {ticker}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {matrixData.tickers.map((tickerRow, rowIndex) => (
                    <tr key={rowIndex}>
                      <td className="correlation-matrix-row-header">
                        {tickerRow}
                      </td>
                      {matrixData.matrix[rowIndex].map((value, colIndex) => (
                        <td 
                          key={colIndex}
                          onClick={() => handleCellClick(tickerRow, matrixData.tickers[colIndex], value)}
                          className={`correlation-matrix-cell ${rowIndex === colIndex ? 'diagonal' : 'clickable'}`}
                          style={{ 
                            background: getCorrelationColor(value),
                            color: Math.abs(value) > 0.5 ? 'white' : '#333'
                          }}
                        >
                          {value.toFixed(2)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {selectedCell && (
            <div className="card">
              <h3>Detalle de Correlación</h3>
              <div 
                className="correlation-detail-card"
                style={{ 
                  background: getCorrelationColor(selectedCell.value),
                  color: Math.abs(selectedCell.value) > 0.5 ? 'white' : '#333'
                }}
              >
                <div className="correlation-detail-tickers">
                  <strong>{selectedCell.tickerA}</strong> vs <strong>{selectedCell.tickerB}</strong>
                </div>
                <div className="correlation-detail-value">
                  {selectedCell.value.toFixed(4)}
                </div>
                <div className="correlation-detail-label">
                  {getCorrelationLabel(selectedCell.value)}
                </div>
              </div>

              <div className="correlation-interpretation">
                <p><strong>Interpretación:</strong></p>
                <p>
                  {selectedCell.value > 0.7 
                    ? `Los activos ${selectedCell.tickerA} y ${selectedCell.tickerB} tienen una correlación positiva fuerte. Tienden a moverse en la misma dirección. Cuando uno sube, el otro también tiende a subir.`
                    : selectedCell.value > 0.3
                    ? `Los activos ${selectedCell.tickerA} y ${selectedCell.tickerB} tienen una correlación positiva moderada. Hay cierta tendencia a moverse juntos, pero no es muy fuerte.`
                    : selectedCell.value > -0.3
                    ? `Los activos ${selectedCell.tickerA} y ${selectedCell.tickerB} tienen una correlación débil. Sus movimientos son relativamente independientes.`
                    : selectedCell.value > -0.7
                    ? `Los activos ${selectedCell.tickerA} y ${selectedCell.tickerB} tienen una correlación negativa moderada. Tienden a moverse en direcciones opuestas.`
                    : `Los activos ${selectedCell.tickerA} y ${selectedCell.tickerB} tienen una correlación negativa fuerte. Cuando uno sube, el otro tiende a bajar significativamente.`
                  }
                </p>

                <p><strong>Implicaciones para diversificación:</strong></p>
                <p>
                  {Math.abs(selectedCell.value) < 0.3
                    ? 'Excelente para diversificación. Los activos se mueven independientemente, reduciendo el riesgo del portafolio.'
                    : Math.abs(selectedCell.value) < 0.7
                    ? 'Diversificación moderada. Hay cierta relación entre los activos.'
                    : 'Poca diversificación. Los activos están altamente correlacionados y no reducen significativamente el riesgo.'
                  }
                </p>
              </div>
            </div>
          )}

          <div className="card">
            <h3>Guía de Interpretación</h3>
            <div className="correlation-guide-grid">
              <div className="correlation-guide-box guide-strong-positive">
                <strong>0.7 a 1.0</strong>
                <p>
                  Correlación positiva fuerte. Los activos se mueven juntos.
                </p>
              </div>

              <div className="correlation-guide-box guide-moderate-positive">
                <strong>0.3 a 0.7</strong>
                <p>
                  Correlación positiva moderada. Cierta tendencia a moverse juntos.
                </p>
              </div>

              <div className="correlation-guide-box guide-weak">
                <strong>-0.3 a 0.3</strong>
                <p>
                  Correlación débil. Movimientos independientes.
                </p>
              </div>

              <div className="correlation-guide-box guide-moderate-negative">
                <strong>-0.7 a -0.3</strong>
                <p>
                  Correlación negativa moderada. Tienden a moverse en direcciones opuestas.
                </p>
              </div>

              <div className="correlation-guide-box guide-strong-negative">
                <strong>-1.0 a -0.7</strong>
                <p>
                  Correlación negativa fuerte. Se mueven en direcciones opuestas.
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <h3>Fórmula de Correlación de Pearson</h3>
            <div className="correlation-formula">
              <p className="formula-text">
                r = Σ((x_i - μ_x)(y_i - μ_y)) / (σ_x × σ_y)
              </p>
              <p className="formula-description">
                Donde:<br/>
                • r = coeficiente de correlación [-1, 1]<br/>
                • μ_x, μ_y = medias de las series<br/>
                • σ_x, σ_y = desviaciones estándar<br/>
                • Complejidad: O(n) por par de activos<br/>
                • Total: O(m² × n) para m activos
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default CorrelationMatrix;
