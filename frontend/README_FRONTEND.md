# Frontend - BVC Analysis

Aplicación web React para el análisis algorítmico de activos financieros.

## Requisitos Previos

- Node.js 16+ (LTS recomendado)
- npm o yarn
- Backend corriendo en `http://localhost:8000`

## Instalación

```bash
# Desde la carpeta frontend
cd frontend

# Instalar dependencias
npm install
```

## Ejecución

```bash
# Modo desarrollo
npm start
```

La aplicación se abrirá automáticamente en `http://localhost:3000`

## Construcción para Producción

```bash
# Generar build optimizado
npm run build
```

Los archivos optimizados estarán en la carpeta `build/`

## Estructura del Proyecto

```
frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── Dashboard.js              ← Dashboard principal
│   │   ├── SimilarityAnalysis.js     ← Análisis de similitud
│   │   ├── VolatilityAnalysis.js     ← Análisis de volatilidad
│   │   ├── PatternAnalysis.js        ← Detección de patrones
│   │   └── CorrelationMatrix.js      ← Matriz de correlación
│   ├── App.js                        ← Componente principal
│   ├── App.css                       ← Estilos globales
│   ├── index.js                      ← Punto de entrada
│   └── index.css                     ← Estilos base
├── package.json
└── README_FRONTEND.md
```

## Funcionalidades

### 1. Dashboard Principal
- Vista general del sistema
- Lista de activos del portafolio
- Estadísticas generales
- Descarga de reporte PDF

### 2. Análisis de Similitud
- Comparación entre dos activos
- 4 algoritmos: Euclidiana, Pearson, Coseno, DTW
- Visualización de resultados
- Interpretación automática

### 3. Análisis de Volatilidad
- Clasificación de riesgo (Conservador, Moderado, Agresivo)
- Tabla ordenada por volatilidad
- Filtros por nivel de riesgo
- Estadísticas del portafolio

### 4. Análisis de Patrones
- Detección de días consecutivos al alza
- Detección de picos de volatilidad
- Algoritmos de ventanas deslizantes
- Top ocurrencias de cada patrón

### 5. Matriz de Correlación
- Matriz completa de correlaciones
- Heatmap interactivo
- Detalles al hacer clic
- Guía de interpretación

## Tecnologías Utilizadas

- **React 19** - Framework de UI
- **Axios** - Cliente HTTP
- **CSS3** - Estilos (sin librerías adicionales)
- **Create React App** - Configuración base

## Configuración de API

El frontend se conecta al backend en `http://localhost:8000` por defecto.

Para cambiar la URL del backend, edita la constante en cada componente:

```javascript
const API_BASE_URL = 'http://localhost:8000';
```

O crea un archivo `.env` en la raíz del frontend:

```env
REACT_APP_API_URL=http://localhost:8000
```

Y usa:

```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

## Solución de Problemas

### Error de CORS

Si ves errores de CORS, asegúrate de que el backend tenga configurado:

```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Backend no responde

1. Verifica que el backend esté corriendo:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. Verifica que esté en el puerto 8000:
   ```
   http://localhost:8000/health
   ```

### Dependencias faltantes

Si hay errores de módulos faltantes:

```bash
rm -rf node_modules package-lock.json
npm install
```

## Scripts Disponibles

- `npm start` - Inicia el servidor de desarrollo
- `npm run build` - Crea build de producción
- `npm test` - Ejecuta tests
- `npm run eject` - Expone configuración (irreversible)

## Navegadores Soportados

- Chrome (últimas 2 versiones)
- Firefox (últimas 2 versiones)
- Safari (últimas 2 versiones)
- Edge (últimas 2 versiones)

## Notas de Desarrollo

- El frontend es completamente independiente del backend
- Todas las llamadas a la API son asíncronas
- Los componentes manejan sus propios estados de carga y error
- No se usan librerías de gráficos (visualizaciones con CSS)

## Próximas Mejoras

- [ ] Gráficos de velas (candlestick) con Chart.js
- [ ] Exportación de datos a CSV
- [ ] Modo oscuro
- [ ] Responsive mejorado para móviles
- [ ] Caché de resultados
- [ ] Animaciones de transición

---

**Versión:** 1.0.0  
**Última actualización:** Mayo 12, 2026
