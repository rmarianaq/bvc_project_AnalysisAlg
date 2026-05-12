import React, { useState } from 'react';
import './App.css';
import Dashboard from './components/Dashboard/Dashboard';
import SimilarityAnalysis from './components/SimilarityAnalysis/SimilarityAnalysis';
import VolatilityAnalysis from './components/VolatilityAnalysis/VolatilityAnalysis';
import PatternAnalysis from './components/PatternAnalysis/PatternAnalysis';
import CorrelationMatrix from './components/CorrelationMatrix/CorrelationMatrix';
import CandlestickChart from './components/CandlestickChart/CandlestickChart';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'similarity':
        return <SimilarityAnalysis />;
      case 'volatility':
        return <VolatilityAnalysis />;
      case 'patterns':
        return <PatternAnalysis />;
      case 'correlation':
        return <CorrelationMatrix />;
      case 'candlestick':
        return <CandlestickChart />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-content">
          <h1>📊 BVC Analysis</h1>
          <p className="subtitle">Análisis Algorítmico de Activos Financieros</p>
        </div>
      </header>

      <nav className="navigation">
        <button
          className={activeTab === 'dashboard' ? 'nav-button active' : 'nav-button'}
          onClick={() => setActiveTab('dashboard')}
        >
          🏠 Dashboard
        </button>
        <button
          className={activeTab === 'similarity' ? 'nav-button active' : 'nav-button'}
          onClick={() => setActiveTab('similarity')}
        >
          🔍 Similitud
        </button>
        <button
          className={activeTab === 'volatility' ? 'nav-button active' : 'nav-button'}
          onClick={() => setActiveTab('volatility')}
        >
          📈 Volatilidad
        </button>
        <button
          className={activeTab === 'patterns' ? 'nav-button active' : 'nav-button'}
          onClick={() => setActiveTab('patterns')}
        >
          🎯 Patrones
        </button>
        <button
          className={activeTab === 'correlation' ? 'nav-button active' : 'nav-button'}
          onClick={() => setActiveTab('correlation')}
        >
          🔗 Correlación
        </button>
        <button
          className={activeTab === 'candlestick' ? 'nav-button active' : 'nav-button'}
          onClick={() => setActiveTab('candlestick')}
        >
          📊 Velas
        </button>
      </nav>

      <main className="main-content">
        {renderContent()}
      </main>

      <footer className="App-footer">
        <p>Universidad del Quindío - Análisis de Algoritmos</p>
        <p>Proyecto: Análisis Algorítmico BVC | 2026</p>
      </footer>
    </div>
  );
}

export default App;
