import React, { useState } from 'react';
import axios from 'axios';
import './SortingBenchmark.css';
import { API_BASE_URL } from '../../config';

function SortingBenchmark() {
  const [benchmarkData, setBenchmarkData] = useState(null);
  const [topVolumeData, setTopVolumeData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runBenchmark = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Ejecutar benchmark
      const benchmarkResponse = await axios.get(`${API_BASE_URL}/sorting/benchmark`);
      setBenchmarkData(benchmarkResponse.data);

      // Obtener top volumen
      const volumeResponse = await axios.get(`${API_BASE_URL}/sorting/top-volume?limit=15`);
      setTopVolumeData(volumeResponse.data);

      setLoading(false);
    } catch (err) {
      setError('Error al ejecutar el benchmark. Esto puede tardar varios segundos.');
      setLoading(false);
    }
  };

  const getComplexityColor = (algorithm) => {
    const complexityMap = {
      'TimSort': '#378ADD',
      'QuickSort': '#378ADD',
      'HeapSort': '#378ADD',
      'Tree Sort': '#378ADD',
      'Bitonic Sort': '#BA7517',
      'RadixSort': '#1D9E75',
      'Bucket Sort': '#1D9E75',
      'Pigeonhole Sort': '#1D9E75',
      'Comb Sort': '#A32D2D',
      'Selection Sort': '#A32D2D',
      'Gnome Sort': '#A32D2D',
      'Binary Insertion Sort': '#A32D2D'
    };
    return complexityMap[algorithm] || '#888888';
  };

  const getComplexityLabel = (algorithm) => {
    const complexityMap = {
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
    };
    return complexityMap[algorithm] || 'O(?)';
  };

  const renderBarChart = () => {
    if (!benchmarkData || !benchmarkData.results) return null;

    const results = benchmarkData.results;
    const maxTime = Math.max(...results.map(r => r.time_seconds));

    return (
      <div className="benchmark-chart">
        {results.map((result, index) => {
          const widthPercent = (result.time_seconds / maxTime) * 100;
          const color = getComplexityColor(result.algorithm);

          return (
            <div key={index} className="benchmark-bar-row">
              <div className="benchmark-rank">{index + 1}</div>
              <div className="benchmark-algorithm-name">{result.algorithm}</div>
              <div className="benchmark-bar-container">
                <div 
                  className="benchmark-bar"
                  style={{ 
                    width: `${widthPercent}%`,
                    backgroundColor: color
                  }}
                >
                  <span className="benchmark-time-label">
                    {result.time_seconds.toFixed(4)}s
                  </span>
                </div>
              </div>
              <div className="benchmark-complexity">
                {getComplexityLabel(result.algorithm)}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="sorting-container">
      <div className="card">
        <h2>Benchmark de Algoritmos de Ordenamiento</h2>
        <p className="sorting-description">
          Análisis comparativo de 12 algoritmos de ordenamiento sobre el dataset financiero unificado.
          Los registros se ordenan por fecha de cotización (ascendente) y precio de cierre (desempate).
        </p>

        <button 
          className="btn btn-primary btn-large" 
          onClick={runBenchmark}
          disabled={loading}
        >
          {loading ? 'Ejecutando Benchmark...' : 'Ejecutar Benchmark'}
        </button>

        {loading && (
          <div className="loading-message">
            <div className="spinner"></div>
            <p>Ejecutando 12 algoritmos de ordenamiento...</p>
            <p className="loading-detail">Esto puede tardar 10-30 segundos dependiendo del tamaño del dataset</p>
          </div>
        )}

        {error && (
          <div className="error sorting-error">
            {error}
          </div>
        )}
      </div>

      {benchmarkData && (
        <>
          <div className="card">
            <h3>Resultados del Benchmark</h3>
            <div className="benchmark-summary">
              <div className="summary-item">
                <span className="summary-label">Dataset:</span>
                <span className="summary-value">{benchmarkData.dataset_size.toLocaleString()} registros</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Algoritmos:</span>
                <span className="summary-value">{benchmarkData.total_algorithms}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Más rápido:</span>
                <span className="summary-value">
                  {benchmarkData.results[0].algorithm} ({benchmarkData.results[0].time_seconds.toFixed(4)}s)
                </span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Más lento:</span>
                <span className="summary-value">
                  {benchmarkData.results[benchmarkData.results.length - 1].algorithm} 
                  ({benchmarkData.results[benchmarkData.results.length - 1].time_seconds.toFixed(4)}s)
                </span>
              </div>
            </div>
          </div>

          <div className="card">
            <h3>Tiempos de Ejecución (Ordenados Ascendentemente)</h3>
            {renderBarChart()}
          </div>

          <div className="card">
            <h3>Tabla Comparativa</h3>
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Algoritmo</th>
                    <th>Complejidad</th>
                    <th>Tamaño</th>
                    <th>Tiempo (s)</th>
                    <th>Tiempo (ms)</th>
                  </tr>
                </thead>
                <tbody>
                  {benchmarkData.results.map((result, index) => (
                    <tr key={index}>
                      <td>{index + 1}</td>
                      <td><strong>{result.algorithm}</strong></td>
                      <td>
                        <span 
                          className="complexity-badge"
                          style={{ backgroundColor: getComplexityColor(result.algorithm) }}
                        >
                          {getComplexityLabel(result.algorithm)}
                        </span>
                      </td>
                      <td>{result.records.toLocaleString()}</td>
                      <td>{result.time_seconds.toFixed(4)}</td>
                      <td>{(result.time_seconds * 1000).toFixed(0)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="card">
            <h3>Análisis de Complejidad</h3>
            <div className="complexity-legend">
              <div className="complexity-item">
                <div className="complexity-color" style={{ backgroundColor: '#1D9E75' }}></div>
                <div className="complexity-info">
                  <strong>O(n + k) / O(nk)</strong>
                  <p>Algoritmos lineales o casi lineales. Muy eficientes para datasets grandes.</p>
                  <p className="complexity-algorithms">Pigeonhole Sort, Bucket Sort, Radix Sort</p>
                </div>
              </div>

              <div className="complexity-item">
                <div className="complexity-color" style={{ backgroundColor: '#378ADD' }}></div>
                <div className="complexity-info">
                  <strong>O(n log n)</strong>
                  <p>Algoritmos eficientes. Balance óptimo entre velocidad y uso de memoria.</p>
                  <p className="complexity-algorithms">TimSort, QuickSort, HeapSort, Tree Sort</p>
                </div>
              </div>

              <div className="complexity-item">
                <div className="complexity-color" style={{ backgroundColor: '#BA7517' }}></div>
                <div className="complexity-info">
                  <strong>O(n log²n)</strong>
                  <p>Complejidad logarítmica cuadrática. Útil para ordenamiento paralelo.</p>
                  <p className="complexity-algorithms">Bitonic Sort</p>
                </div>
              </div>

              <div className="complexity-item">
                <div className="complexity-color" style={{ backgroundColor: '#A32D2D' }}></div>
                <div className="complexity-info">
                  <strong>O(n²)</strong>
                  <p>Algoritmos cuadráticos. Ineficientes para datasets grandes.</p>
                  <p className="complexity-algorithms">Selection Sort, Gnome Sort, Binary Insertion Sort, Comb Sort</p>
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {topVolumeData && (
        <div className="card">
          <h3>Top 15 Días con Mayor Volumen de Negociación</h3>
          <p className="top-volume-description">
            Días ordenados por volumen de negociación (descendente) usando Selection Sort manual.
          </p>
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Fecha</th>
                  <th>Ticker</th>
                  <th>Volumen</th>
                  <th>Precio Cierre</th>
                </tr>
              </thead>
              <tbody>
                {topVolumeData.top_volume_days.map((day, index) => (
                  <tr key={index}>
                    <td>{index + 1}</td>
                    <td>{day.trade_date}</td>
                    <td><strong>{day.ticker}</strong></td>
                    <td className="volume-cell">{day.volume.toLocaleString()}</td>
                    <td className="price-cell">${day.close_price.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {benchmarkData && (
        <div className="card">
          <h3>Conclusiones del Benchmark</h3>
          <div className="conclusions">
            <p>
              <strong>Algoritmo más eficiente:</strong> {benchmarkData.results[0].algorithm} con 
              {' '}{(benchmarkData.results[0].time_seconds * 1000).toFixed(0)} ms para ordenar 
              {' '}{benchmarkData.dataset_size.toLocaleString()} registros.
            </p>

            <p>
              <strong>Diferencia de rendimiento:</strong> El algoritmo más lento 
              ({benchmarkData.results[benchmarkData.results.length - 1].algorithm}) 
              es {(benchmarkData.results[benchmarkData.results.length - 1].time_seconds / 
                  benchmarkData.results[0].time_seconds).toFixed(0)}× más lento que el más rápido.
            </p>

            <p>
              <strong>Observaciones:</strong> Los algoritmos con complejidad O(n log n) como TimSort y QuickSort
              demuestran ser los más eficientes para datasets financieros de este tamaño. Los algoritmos
              cuadráticos O(n²) como Selection Sort y Gnome Sort son significativamente más lentos y no
              son recomendables para datasets grandes.
            </p>

            <p>
              <strong>Criterio de ordenamiento:</strong> Los registros se ordenan primero por fecha de cotización
              (ascendente) y en caso de empate, por precio de cierre. Este criterio permite mantener la
              cronología de los datos financieros mientras se resuelven ambigüedades de manera determinística.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default SortingBenchmark;
