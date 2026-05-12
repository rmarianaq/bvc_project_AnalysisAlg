# Estructura del Frontend - BVC Analysis

## 📁 Organización de Componentes

El frontend está organizado siguiendo las mejores prácticas de React, donde cada componente tiene su propia carpeta con archivos JS y CSS separados.

```
frontend/src/
├── components/
│   ├── Dashboard/
│   │   ├── Dashboard.js          # Componente principal con JSX
│   │   └── Dashboard.css         # Estilos específicos del Dashboard
│   │
│   ├── SimilarityAnalysis/
│   │   ├── SimilarityAnalysis.js # Comparación de similitud entre activos
│   │   └── SimilarityAnalysis.css
│   │
│   ├── VolatilityAnalysis/
│   │   ├── VolatilityAnalysis.js # Análisis de volatilidad y riesgo
│   │   └── VolatilityAnalysis.css
│   │
│   ├── PatternAnalysis/
│   │   ├── PatternAnalysis.js    # Detección de patrones
│   │   └── PatternAnalysis.css
│   │
│   └── CorrelationMatrix/
│       ├── CorrelationMatrix.js  # Matriz de correlación
│       └── CorrelationMatrix.css
│
├── App.js                         # Componente raíz con navegación
├── App.css                        # Estilos globales
└── index.js                       # Punto de entrada

```

## 🎯 Arquitectura de React

### ¿Por qué no hay archivos HTML separados?

React utiliza **JSX (JavaScript XML)**, que permite escribir código similar a HTML dentro de archivos JavaScript. Esta es la arquitectura estándar de React y tiene varias ventajas:

1. **Componentes Reutilizables**: Cada componente encapsula su lógica y presentación
2. **Mantenibilidad**: Todo el código relacionado está junto
3. **Rendimiento**: React optimiza el renderizado del DOM virtual
4. **Type Safety**: Mejor integración con TypeScript y validación

### Estructura de un Componente

Cada componente sigue este patrón:

```javascript
// ComponentName.js
import React, { useState } from 'react';
import axios from 'axios';
import './ComponentName.css';  // Importa sus propios estilos

function ComponentName() {
  // 1. Estado del componente
  const [data, setData] = useState(null);
  
  // 2. Funciones y lógica
  const fetchData = async () => {
    // Lógica de negocio
  };
  
  // 3. JSX (el "HTML" de React)
  return (
    <div className="component-container">
      <h2>Título</h2>
      {/* Contenido dinámico */}
    </div>
  );
}

export default ComponentName;
```

## 📊 Componentes Implementados

### 1. Dashboard (`Dashboard/`)
- **Propósito**: Vista principal con estadísticas generales
- **Características**:
  - Estado del sistema y base de datos
  - Lista de activos del portafolio
  - Descarga de reportes PDF
  - Información del proyecto

### 2. SimilarityAnalysis (`SimilarityAnalysis/`)
- **Propósito**: Comparar similitud entre dos activos
- **Algoritmos**:
  - Distancia Euclidiana (O(n))
  - Correlación de Pearson (O(n))
  - Similitud por Coseno (O(n))
  - Dynamic Time Warping (O(n²))

### 3. VolatilityAnalysis (`VolatilityAnalysis/`)
- **Propósito**: Análisis de volatilidad y clasificación de riesgo
- **Características**:
  - Volatilidad anualizada (σ_anual = σ_diaria × √252)
  - Clasificación: Conservador, Moderado, Agresivo
  - Filtros por nivel de riesgo
  - Visualización con barras de progreso

### 4. PatternAnalysis (`PatternAnalysis/`)
- **Propósito**: Detección de patrones en series temporales
- **Patrones**:
  - Días consecutivos al alza (ventana deslizante)
  - Picos de volatilidad (threshold × σ_global)
- **Complejidad**: O(n × w)

### 5. CorrelationMatrix (`CorrelationMatrix/`)
- **Propósito**: Matriz de correlación completa del portafolio
- **Características**:
  - Matriz interactiva con colores
  - Click en celdas para detalles
  - Interpretación de correlaciones
  - Guía de diversificación

## 🎨 Estilos CSS

Cada componente tiene su propio archivo CSS con:

- **Clases específicas**: Prefijadas con el nombre del componente
- **Responsive Design**: Media queries para móviles
- **Colores temáticos**: Consistentes con el diseño general
- **Animaciones**: Transiciones suaves

Ejemplo de nomenclatura:
```css
/* Dashboard.css */
.dashboard-container { }
.dashboard-stats-grid { }
.dashboard-stat-card { }

/* SimilarityAnalysis.css */
.similarity-container { }
.similarity-form-grid { }
.similarity-metric-card { }
```

## 🔄 Flujo de Datos

```
Usuario → Componente → API Backend → Base de Datos
                ↓
            Estado (useState)
                ↓
            Re-renderizado
                ↓
            Vista Actualizada
```

## 🚀 Ejecución

```bash
# Instalar dependencias
cd frontend
npm install

# Iniciar servidor de desarrollo
npm start

# El frontend se ejecuta en http://localhost:3000
# El backend debe estar corriendo en http://localhost:8000
```

## 📦 Dependencias Principales

- **React**: Framework de UI
- **axios**: Cliente HTTP para llamadas a la API
- **react-scripts**: Herramientas de desarrollo

## 🔧 Configuración

El archivo `package.json` contiene:
- Scripts de ejecución
- Dependencias del proyecto
- Configuración de build

## 📝 Notas Importantes

1. **No hay archivos HTML separados**: React usa JSX dentro de los archivos .js
2. **Single Page Application (SPA)**: Todo se renderiza en `public/index.html`
3. **Componentes funcionales**: Usamos hooks (useState, useEffect) en lugar de clases
4. **Estilos modulares**: Cada componente importa su propio CSS
5. **API REST**: Comunicación con backend mediante axios

## 🎓 Cumplimiento Académico

Esta estructura cumple con los requisitos del proyecto:
- ✅ Separación de responsabilidades (componentes independientes)
- ✅ Código organizado y mantenible
- ✅ Documentación clara de la arquitectura
- ✅ Implementación manual de la lógica (no librerías de alto nivel)
- ✅ Integración completa con el backend desarrollado

---

**Universidad del Quindío**  
**Análisis de Algoritmos - 2026**  
**Proyecto: Análisis Algorítmico de Activos Financieros BVC**
