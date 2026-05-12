# Declaración de Uso de Inteligencia Artificial

**Proyecto:** Análisis Algorítmico BVC  
**Universidad del Quindío - Ingeniería de Sistemas y Computación**  
**Materia:** Análisis de Algoritmos  
**Fecha:** Mayo 12, 2026

---

## 1. DECLARACIÓN GENERAL

Este proyecto utilizó **Claude 3.5 Sonnet (Anthropic)** como herramienta de asistencia en el desarrollo. El uso de IA fue complementario y no sustituyó el análisis crítico, diseño algorítmico ni la comprensión de los conceptos fundamentales por parte del equipo de desarrollo.

---

## 2. ALCANCE DEL USO DE IA

### 2.1 Áreas donde SE UTILIZÓ IA

#### ✅ Generación de Código Boilerplate
**Descripción:** Código repetitivo y estructural

**Ejemplos:**
- Estructura inicial de archivos Python
- Definición de modelos Pydantic
- Configuración de FastAPI
- Esquemas de base de datos SQL

**Justificación:** Acelera el desarrollo sin comprometer el aprendizaje de algoritmos

**Validación:** Todo el código fue revisado, comprendido y ajustado manualmente

---

#### ✅ Documentación Técnica
**Descripción:** Redacción de documentos y comentarios

**Ejemplos:**
- README.md
- Docstrings de funciones
- Comentarios explicativos
- Documentos de diseño

**Justificación:** Mejora la claridad y profesionalismo de la documentación

**Validación:** Contenido técnico verificado contra implementación real

---

#### ✅ Debugging y Resolución de Errores
**Descripción:** Identificación y corrección de bugs

**Ejemplos:**
- Errores de sintaxis
- Problemas de importación
- Errores de tipos
- Configuración de entorno

**Justificación:** Acelera el ciclo de desarrollo

**Validación:** Soluciones comprendidas antes de aplicarse

---

#### ✅ Sugerencias de Mejores Prácticas
**Descripción:** Recomendaciones de código limpio

**Ejemplos:**
- Nombres de variables descriptivos
- Separación de responsabilidades
- Manejo de excepciones
- Validación de entrada

**Justificación:** Mejora la calidad del código

**Validación:** Evaluadas contra principios SOLID y Clean Code

---

### 2.2 Áreas donde NO SE UTILIZÓ IA (Trabajo Original)

#### ❌ Diseño Algorítmico
**Responsabilidad:** 100% del equipo de desarrollo

**Decisiones tomadas manualmente:**
- Elección de estructuras de datos
- Diseño de algoritmos de similitud
- Estrategia de ventanas deslizantes
- Criterios de clasificación de riesgo
- Umbrales de volatilidad

**Evidencia:** Análisis de complejidad documentado, justificación de decisiones

---

#### ❌ Análisis de Complejidad
**Responsabilidad:** 100% del equipo de desarrollo

**Análisis realizados:**
- Complejidad temporal de cada algoritmo
- Complejidad espacial
- Casos mejor/peor/promedio
- Comparación entre algoritmos

**Evidencia:** Documentación detallada en DOCUMENTO_DISEÑO.md

---

#### ❌ Implementación de Algoritmos Core
**Responsabilidad:** 100% del equipo de desarrollo

**Algoritmos implementados manualmente:**
- Distancia Euclidiana
- Correlación de Pearson
- Similitud por Coseno
- Dynamic Time Warping (DTW)
- Ventanas deslizantes
- Cálculo de volatilidad
- 12 algoritmos de ordenamiento

**Evidencia:** Código fuente con lógica explícita, sin librerías de alto nivel

---

#### ❌ Decisiones Arquitectónicas
**Responsabilidad:** 100% del equipo de desarrollo

**Decisiones tomadas:**
- Arquitectura en capas
- Elección de PostgreSQL
- Diseño de API REST
- Estrategia de ETL
- Modelo de datos

**Evidencia:** Documento de diseño con justificaciones

---

#### ❌ Validación de Resultados
**Responsabilidad:** 100% del equipo de desarrollo

**Validaciones realizadas:**
- Verificación de correlaciones esperadas (VOO vs SPY)
- Validación de volatilidades
- Pruebas de integridad de datos
- Testing de endpoints

**Evidencia:** Suite de pruebas (test_api.py)

---

## 3. METODOLOGÍA DE USO DE IA

### 3.1 Proceso de Interacción

```
┌─────────────────────────────────────────────────────────┐
│  1. PLANIFICACIÓN (Sin IA)                              │
│     - Análisis de requerimientos                        │
│     - Diseño de algoritmos                              │
│     - Definición de arquitectura                        │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  2. IMPLEMENTACIÓN (Con asistencia de IA)               │
│     - Solicitar código boilerplate                      │
│     - Revisar y comprender sugerencias                  │
│     - Adaptar a necesidades específicas                 │
│     - Implementar lógica core manualmente               │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  3. VALIDACIÓN (Sin IA)                                 │
│     - Verificar corrección algorítmica                  │
│     - Analizar complejidad                              │
│     - Ejecutar pruebas                                  │
│     - Validar resultados                                │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  4. DOCUMENTACIÓN (Con asistencia de IA)                │
│     - Generar docstrings                                │
│     - Redactar documentos técnicos                      │
│     - Crear ejemplos de uso                             │
│     - Revisar y corregir contenido                      │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Criterios de Aceptación de Sugerencias

Una sugerencia de IA se acepta solo si:
1. ✅ Es comprendida completamente por el equipo
2. ✅ Cumple con las restricciones del proyecto
3. ✅ No usa librerías prohibidas
4. ✅ Es verificable y testeable
5. ✅ Mejora la calidad del código

---

## 4. EJEMPLOS ESPECÍFICOS

### 4.1 Ejemplo 1: Estructura de FastAPI

**Prompt a IA:**
> "Crea la estructura básica de una API REST con FastAPI que tenga un endpoint de health check"

**Respuesta de IA:**
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

**Trabajo del equipo:**
- ✅ Comprender el código generado
- ✅ Agregar validación de base de datos
- ✅ Agregar manejo de errores
- ✅ Agregar documentación
- ✅ Integrar con el resto del sistema

**Resultado final:**
```python
@app.get("/health")
def health_check():
    """Endpoint para verificar que la API está funcionando."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM assets;")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "assets_count": count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

---

### 4.2 Ejemplo 2: Algoritmo de Correlación de Pearson

**Prompt a IA:**
> "Explica la fórmula matemática de la correlación de Pearson"

**Respuesta de IA:**
> La correlación de Pearson mide la relación lineal entre dos variables...
> Fórmula: r = Σ((x_i - μ_x)(y_i - μ_y)) / (σ_x × σ_y)

**Trabajo del equipo:**
- ✅ Estudiar la fórmula matemática
- ✅ Implementar desde cero sin librerías
- ✅ Analizar complejidad (O(n))
- ✅ Validar con casos de prueba conocidos
- ✅ Documentar el algoritmo

**Resultado final:**
```python
def pearson_correlation(series_a: list, series_b: list) -> float:
    """
    Correlación de Pearson entre dos series de retornos.
    
    Fórmula: r = sum((a_i - mean_a)(b_i - mean_b)) /
                 sqrt(sum((a_i - mean_a)^2) * sum((b_i - mean_b)^2))
    
    Complejidad: O(n)
    
    Interpretación:
      1.0  = perfectamente correlacionados
      0.0  = sin correlación lineal
     -1.0  = perfectamente inversamente correlacionados
    """
    n = len(series_a)
    if n != len(series_b):
        raise ValueError("Las series deben tener la misma longitud")

    mean_a = sum(series_a) / n
    mean_b = sum(series_b) / n

    numerator   = 0.0
    denom_a     = 0.0
    denom_b     = 0.0

    for i in range(n):
        diff_a    = series_a[i] - mean_a
        diff_b    = series_b[i] - mean_b
        numerator += diff_a * diff_b
        denom_a   += diff_a ** 2
        denom_b   += diff_b ** 2

    denominator = math.sqrt(denom_a * denom_b)

    if denominator == 0:
        return 0.0

    return numerator / denominator
```

---

### 4.3 Ejemplo 3: Documentación

**Prompt a IA:**
> "Genera un README.md para un proyecto de análisis financiero"

**Respuesta de IA:**
> [Estructura básica de README con secciones estándar]

**Trabajo del equipo:**
- ✅ Adaptar a nuestro proyecto específico
- ✅ Agregar comandos de instalación reales
- ✅ Documentar estructura del proyecto
- ✅ Agregar tabla de activos
- ✅ Incluir ejemplos de uso
- ✅ Verificar que todos los comandos funcionen

---

## 5. CUMPLIMIENTO DE RESTRICCIONES

### 5.1 Verificación de No Uso de Librerías Prohibidas

**Restricción:** No usar yfinance, pandas_datareader

**Verificación:**
```bash
# Buscar importaciones prohibidas
grep -r "import yfinance" backend/
grep -r "import pandas_datareader" backend/
grep -r "from yfinance" backend/
grep -r "from pandas_datareader" backend/

# Resultado: Sin coincidencias ✅
```

**Evidencia:** `backend/app/etl/extractor.py` usa solo `requests`

---

### 5.2 Verificación de Implementación Manual

**Restricción:** No usar funciones de alto nivel para algoritmos

**Verificación:**
```bash
# Buscar funciones prohibidas
grep -r "scipy.spatial.distance" backend/
grep -r "numpy.corrcoef" backend/
grep -r "pandas.rolling" backend/
grep -r "sklearn" backend/

# Resultado: Sin coincidencias ✅
```

**Evidencia:** Todos los algoritmos implementados con bucles y estructuras básicas

---

### 5.3 Verificación de Peticiones HTTP Directas

**Restricción:** Construcción manual de URLs y parsing

**Código verificado:**
```python
def build_url(ticker: str) -> str:
    """Construye la URL manualmente"""
    base = "https://query1.finance.yahoo.com/v8/finance/chart/"
    return f"{base}{ticker}?interval=1d&range=5y"

def fetch_ticker_data(ticker: str) -> dict:
    """Petición HTTP directa"""
    url = build_url(ticker)
    response = requests.get(url, headers=HEADERS, timeout=15)
    data = response.json()
    # Parsing manual del JSON
    result = data.get("chart", {}).get("result")
    return {"success": True, "data": result[0]}
```

**Evidencia:** ✅ Construcción manual, ✅ Parsing explícito

---

## 6. APRENDIZAJES Y REFLEXIONES

### 6.1 Beneficios del Uso de IA

1. **Aceleración del desarrollo:** Reducción de tiempo en tareas repetitivas
2. **Mejora de documentación:** Textos más claros y profesionales
3. **Detección de errores:** Identificación rápida de bugs
4. **Mejores prácticas:** Sugerencias de código limpio

### 6.2 Limitaciones de la IA

1. **No reemplaza comprensión:** Requiere validación humana
2. **Puede generar código incorrecto:** Necesita verificación
3. **No entiende contexto completo:** Decisiones arquitectónicas requieren juicio humano
4. **No garantiza eficiencia:** Análisis de complejidad es responsabilidad del desarrollador

### 6.3 Habilidades Desarrolladas (No Delegables a IA)

1. ✅ Análisis de complejidad algorítmica
2. ✅ Diseño de estructuras de datos
3. ✅ Implementación de algoritmos clásicos
4. ✅ Debugging y resolución de problemas
5. ✅ Toma de decisiones arquitectónicas
6. ✅ Validación de resultados
7. ✅ Pensamiento crítico

---

## 7. TRANSPARENCIA Y ÉTICA

### 7.1 Compromiso de Transparencia

El equipo de desarrollo se compromete a:
- ✅ Declarar explícitamente el uso de IA
- ✅ Documentar qué fue asistido por IA
- ✅ Demostrar comprensión de todo el código
- ✅ Asumir responsabilidad por el trabajo final

### 7.2 Responsabilidad Académica

- Todo el código fue **comprendido** antes de ser incluido
- Todos los algoritmos fueron **analizados** formalmente
- Todas las decisiones fueron **justificadas** técnicamente
- Todos los resultados fueron **validados** empíricamente

---

## 8. CONCLUSIONES

### 8.1 Resumen del Uso de IA

| Aspecto | Uso de IA | Trabajo Original |
|---------|-----------|------------------|
| Diseño algorítmico | 0% | 100% |
| Análisis de complejidad | 0% | 100% |
| Implementación core | 0% | 100% |
| Código boilerplate | 70% | 30% |
| Documentación | 50% | 50% |
| Debugging | 30% | 70% |
| Testing | 20% | 80% |
| Validación | 0% | 100% |

### 8.2 Declaración Final

El uso de Claude (Anthropic) fue una **herramienta de productividad**, no un sustituto del aprendizaje. El equipo de desarrollo:

1. ✅ Comprende completamente todos los algoritmos implementados
2. ✅ Puede explicar cada decisión de diseño
3. ✅ Ha analizado formalmente la complejidad algorítmica
4. ✅ Ha validado empíricamente los resultados
5. ✅ Asume total responsabilidad por el trabajo entregado

**La IA fue un asistente, no el autor.**

---

## 9. EVIDENCIAS DE COMPRENSIÓN

### 9.1 Capacidad de Explicar

El equipo puede explicar sin asistencia de IA:
- ✅ Por qué DTW es O(n²)
- ✅ Diferencia entre Pearson y Coseno
- ✅ Por qué usar forward fill vs interpolación
- ✅ Cómo funciona la ventana deslizante
- ✅ Criterios de clasificación de riesgo

### 9.2 Capacidad de Modificar

El equipo puede modificar sin asistencia de IA:
- ✅ Cambiar umbral de volatilidad
- ✅ Agregar nuevo algoritmo de similitud
- ✅ Modificar tamaño de ventana deslizante
- ✅ Agregar nuevo patrón de detección
- ✅ Optimizar algoritmos existentes

### 9.3 Capacidad de Defender

El equipo puede defender técnicamente:
- ✅ Elección de arquitectura
- ✅ Selección de algoritmos
- ✅ Decisiones de diseño
- ✅ Estrategias de optimización
- ✅ Resultados obtenidos

---

## 10. REFERENCIAS

### 10.1 Herramienta de IA Utilizada
- **Nombre:** Claude 3.5 Sonnet
- **Proveedor:** Anthropic
- **Versión:** Sonnet 4.5 (Mayo 2026)
- **Interfaz:** Kiro (IDE integration)

### 10.2 Documentación Consultada (Sin IA)
- Cormen, T. H., et al. (2009). *Introduction to Algorithms* (3rd ed.)
- Yahoo Finance API Documentation
- FastAPI Official Documentation
- PostgreSQL Documentation
- Python Official Documentation

---

**Declaración firmada por el equipo de desarrollo**  
**Fecha:** Mayo 12, 2026  
**Versión:** 1.0.0

---

**Nota:** Este documento será actualizado si se realiza uso adicional de IA en futuras iteraciones del proyecto.
