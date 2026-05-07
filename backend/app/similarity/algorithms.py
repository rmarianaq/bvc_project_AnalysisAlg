import math


def euclidean_distance(series_a: list, series_b: list) -> float:
    """
    Distancia euclidiana entre dos series de retornos.
    
    Fórmula: d = sqrt( sum( (a_i - b_i)^2 ) )
    
    Complejidad: O(n)
    
    Interpretación: mientras más cercano a 0, más similares.
    No tiene límite superior — depende de la magnitud de los retornos.
    """
    if len(series_a) != len(series_b):
        raise ValueError("Las series deben tener la misma longitud")

    total = 0.0
    for i in range(len(series_a)):
        total += (series_a[i] - series_b[i]) ** 2

    return math.sqrt(total)


def pearson_correlation(series_a: list, series_b: list) -> float:
    """
    Correlación de Pearson entre dos series de retornos.
    
    Fórmula: r = sum((a_i - mean_a)(b_i - mean_b)) /
                 sqrt(sum((a_i - mean_a)^2) * sum((b_i - mean_b)^2))
    
    Complejidad: O(n)
    
    Interpretación:
      1.0  = perfectamente correlacionados (se mueven igual)
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


def cosine_similarity(series_a: list, series_b: list) -> float:
    """
    Similitud por coseno entre dos vectores de retornos.
    
    Fórmula: cos(θ) = (A · B) / (||A|| * ||B||)
    
    Complejidad: O(n)
    
    Interpretación:
      1.0  = misma dirección (muy similares)
      0.0  = perpendiculares (sin relación)
     -1.0  = dirección opuesta
    
    Diferencia con Pearson: no resta la media, mide
    la orientación del vector, no la correlación lineal.
    """
    if len(series_a) != len(series_b):
        raise ValueError("Las series deben tener la misma longitud")

    dot_product = 0.0
    norm_a      = 0.0
    norm_b      = 0.0

    for i in range(len(series_a)):
        dot_product += series_a[i] * series_b[i]
        norm_a      += series_a[i] ** 2
        norm_b      += series_b[i] ** 2

    denominator = math.sqrt(norm_a) * math.sqrt(norm_b)

    if denominator == 0:
        return 0.0

    return dot_product / denominator


def dtw_distance(series_a: list, series_b: list) -> float:
    """
    Dynamic Time Warping — distancia entre dos series temporales.
    
    A diferencia de la euclidiana, DTW permite alinear series
    que están desfasadas en el tiempo. Busca el camino de menor
    costo acumulado a través de una matriz de distancias.
    
    Fórmula recursiva:
      dtw[i][j] = |a_i - b_j| + min(dtw[i-1][j],
                                     dtw[i][j-1],
                                     dtw[i-1][j-1])
    
    Complejidad: O(n * m) tiempo y espacio
    
    Interpretación: igual que euclidiana, más cercano a 0 = más similar.
    """
    n = len(series_a)
    m = len(series_b)

    # Matriz de costos acumulados inicializada con infinito
    dtw = [[float('inf')] * (m + 1) for _ in range(n + 1)]
    dtw[0][0] = 0.0

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost       = abs(series_a[i - 1] - series_b[j - 1])
            dtw[i][j]  = cost + min(
                dtw[i - 1][j],      # inserción
                dtw[i][j - 1],      # eliminación
                dtw[i - 1][j - 1]   # coincidencia
            )

    return dtw[n][m]