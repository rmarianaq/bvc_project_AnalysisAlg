"""
Implementación manual de 12 algoritmos de ordenamiento.
Todos ordenan una lista de registros financieros por:
  1. trade_date  (criterio principal)
  2. close_price (criterio secundario, cuando fecha es igual)

IMPORTANTE: Ningún algoritmo usa funciones de alto nivel
como sorted() o list.sort(). Todo es implementado desde cero
usando estructuras básicas del lenguaje.
"""


def compare(a, b) -> int:
    """
    Función de comparación entre dos registros financieros.
    Retorna:
      -1 si a < b  (a va antes)
       0 si a == b
       1 si a > b  (a va después)

    Criterio 1: trade_date
    Criterio 2: close_price (desempate)
    """
    date_a = str(a["trade_date"])
    date_b = str(b["trade_date"])

    if date_a < date_b:
        return -1
    elif date_a > date_b:
        return 1
    else:
        # Fechas iguales → desempate por precio de cierre
        price_a = float(a["close_price"]) if a["close_price"] else 0.0
        price_b = float(b["close_price"]) if b["close_price"] else 0.0

        if price_a < price_b:
            return -1
        elif price_a > price_b:
            return 1
        return 0


# ═══════════════════════════════════════════════════════
# 1. SELECTION SORT — O(n²)
# Busca el mínimo en cada iteración y lo coloca al frente
# ═══════════════════════════════════════════════════════
def selection_sort(data: list) -> list:
    arr = data[:]  # Copia para no modificar el original
    n   = len(arr)

    for i in range(n):
        # Asumimos que el mínimo está en la posición i
        min_idx = i

        # Buscamos si hay algún elemento menor en el resto
        for j in range(i + 1, n):
            if compare(arr[j], arr[min_idx]) < 0:
                min_idx = j

        # Intercambiamos el mínimo encontrado con la posición i
        arr[i], arr[min_idx] = arr[min_idx], arr[i]

    return arr


# ═══════════════════════════════════════════════════════
# 2. GNOME SORT — O(n²)
# Avanza si el orden es correcto, retrocede si no
# ═══════════════════════════════════════════════════════
def gnome_sort(data: list) -> list:
    arr = data[:]
    n   = len(arr)
    i   = 0

    while i < n:
        if i == 0 or compare(arr[i], arr[i - 1]) >= 0:
            # Está en orden correcto → avanzar
            i += 1
        else:
            # Está en orden incorrecto → intercambiar y retroceder
            arr[i], arr[i - 1] = arr[i - 1], arr[i]
            i -= 1

    return arr


# ═══════════════════════════════════════════════════════
# 3. BINARY INSERTION SORT — O(n²) tiempo, O(n log n) comparaciones
# Usa búsqueda binaria para encontrar la posición de inserción
# ═══════════════════════════════════════════════════════
def binary_insertion_sort(data: list) -> list:
    arr = data[:]
    n   = len(arr)

    for i in range(1, n):
        key  = arr[i]
        # Búsqueda binaria en la parte ya ordenada [0..i-1]
        left  = 0
        right = i - 1

        while left <= right:
            mid = (left + right) // 2
            if compare(key, arr[mid]) < 0:
                right = mid - 1
            else:
                left = mid + 1

        # 'left' es la posición donde debe insertarse 'key'
        # Desplazamos todos los elementos una posición a la derecha
        for j in range(i, left, -1):
            arr[j] = arr[j - 1]

        arr[left] = key

    return arr


# ═══════════════════════════════════════════════════════
# 4. QUICKSORT — O(n log n) promedio, O(n²) peor caso
# Versión iterativa con pila explícita para evitar RecursionError
# ═══════════════════════════════════════════════════════
def quicksort(data: list) -> list:
    arr = data[:]
    n   = len(arr)

    # Usamos una pila explícita en lugar de recursión
    # Cada elemento de la pila es un par (low, high)
    stack = [(0, n - 1)]

    while stack:
        low, high = stack.pop()

        if low < high:
            pivot_idx = _partition(arr, low, high)

            # Apilamos los dos subarreglos para procesar después
            stack.append((low, pivot_idx - 1))
            stack.append((pivot_idx + 1, high))

    return arr


def _partition(arr: list, low: int, high: int) -> int:
    """
    Coloca el pivote en su posición correcta.
    Usamos mediana de tres para evitar el peor caso O(n²)
    cuando el arreglo ya está ordenado.
    """
    # Mediana de tres: elegimos mejor pivote entre
    # el primero, el del medio y el último
    mid = (low + high) // 2

    # Ordenamos los tres candidatos
    if compare(arr[low], arr[mid]) > 0:
        arr[low], arr[mid] = arr[mid], arr[low]
    if compare(arr[low], arr[high]) > 0:
        arr[low], arr[high] = arr[high], arr[low]
    if compare(arr[mid], arr[high]) > 0:
        arr[mid], arr[high] = arr[high], arr[mid]

    # El pivote es la mediana → lo movemos a high-1
    pivot = arr[mid]
    arr[mid], arr[high] = arr[high], arr[mid]

    i = low - 1
    for j in range(low, high):
        if compare(arr[j], pivot) <= 0:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

# ═══════════════════════════════════════════════════════
# 5. HEAPSORT — O(n log n)
# Construye un Max-Heap y extrae el máximo repetidamente
# ═══════════════════════════════════════════════════════
def heapsort(data: list) -> list:
    arr = data[:]
    n   = len(arr)

    # Fase 1: Construir el Max-Heap
    # Empezamos desde el último nodo interno
    for i in range(n // 2 - 1, -1, -1):
        _heapify(arr, n, i)

    # Fase 2: Extraer elementos del heap uno por uno
    for i in range(n - 1, 0, -1):
        # El máximo está en la raíz (índice 0)
        # Lo movemos al final
        arr[0], arr[i] = arr[i], arr[0]
        # Restauramos la propiedad del heap en el arreglo reducido
        _heapify(arr, i, 0)

    return arr


def _heapify(arr: list, n: int, i: int):
    """
    Mantiene la propiedad del Max-Heap.
    El padre debe ser mayor que sus hijos.
    """
    largest = i          # Asumimos que la raíz es el mayor
    left    = 2 * i + 1  # Hijo izquierdo
    right   = 2 * i + 2  # Hijo derecho

    # ¿El hijo izquierdo es mayor que la raíz?
    if left < n and compare(arr[left], arr[largest]) > 0:
        largest = left

    # ¿El hijo derecho es mayor que el actual mayor?
    if right < n and compare(arr[right], arr[largest]) > 0:
        largest = right

    # Si el mayor no es la raíz, intercambiamos y continuamos
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        _heapify(arr, n, largest)


# ═══════════════════════════════════════════════════════
# 6. TIMSORT — O(n log n)
# Híbrido: Insertion Sort para bloques pequeños + Merge Sort
# ═══════════════════════════════════════════════════════
RUN = 32  # Tamaño del bloque para Insertion Sort

def timsort(data: list) -> list:
    arr = data[:]
    n   = len(arr)

    # Fase 1: Ordenar cada bloque de tamaño RUN con Insertion Sort
    for start in range(0, n, RUN):
        end = min(start + RUN - 1, n - 1)
        _insertion_sort_range(arr, start, end)

    # Fase 2: Fusionar los bloques ordenados
    size = RUN
    while size < n:
        for left in range(0, n, 2 * size):
            mid   = min(left + size - 1, n - 1)
            right = min(left + 2 * size - 1, n - 1)
            if mid < right:
                _merge(arr, left, mid, right)
        size *= 2

    return arr


def _insertion_sort_range(arr: list, left: int, right: int):
    """Insertion Sort sobre un rango específico del arreglo."""
    for i in range(left + 1, right + 1):
        key = arr[i]
        j   = i - 1
        while j >= left and compare(arr[j], key) > 0:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key


def _merge(arr: list, left: int, mid: int, right: int):
    """Fusiona dos subarreglos ordenados en uno solo."""
    left_arr  = arr[left:mid + 1]
    right_arr = arr[mid + 1:right + 1]

    i = j = 0
    k = left

    while i < len(left_arr) and j < len(right_arr):
        if compare(left_arr[i], right_arr[j]) <= 0:
            arr[k] = left_arr[i]
            i += 1
        else:
            arr[k] = right_arr[j]
            j += 1
        k += 1

    while i < len(left_arr):
        arr[k] = left_arr[i]
        i += 1
        k += 1

    while j < len(right_arr):
        arr[k] = right_arr[j]
        j += 1
        k += 1


# ═══════════════════════════════════════════════════════
# 7. COMB SORT — O(n log n), peor caso O(n²)
# Bubble Sort con gaps grandes que se reducen gradualmente
# ═══════════════════════════════════════════════════════
def comb_sort(data: list) -> list:
    arr      = data[:]
    n        = len(arr)
    gap      = n
    shrink   = 1.3  # Factor de reducción del gap
    sorted_  = False

    while not sorted_:
        # Reducir el gap
        gap = int(gap / shrink)
        if gap <= 1:
            gap     = 1
            sorted_ = True  # Asumimos que está ordenado

        i = 0
        while i + gap < n:
            if compare(arr[i], arr[i + gap]) > 0:
                arr[i], arr[i + gap] = arr[i + gap], arr[i]
                sorted_ = False  # Hubo intercambio → no está ordenado
            i += 1

    return arr


# ═══════════════════════════════════════════════════════
# 8. TREE SORT — O(n log n) promedio , peor caso O(n²)
# Versión iterativa para evitar RecursionError con datasets grandes
# ═══════════════════════════════════════════════════════
class BSTNode:
    """Nodo de un árbol binario de búsqueda."""
    def __init__(self, data):
        self.data  = data
        self.left  = None
        self.right = None


def _bst_insert_iterative(root, data):
    """
    Inserción iterativa en BST.
    Evita RecursionError en datasets grandes.
    """
    new_node = BSTNode(data)
    if root is None:
        return new_node

    current = root
    while True:
        if compare(data, current.data) < 0:
            if current.left is None:
                current.left = new_node
                break
            current = current.left
        else:
            if current.right is None:
                current.right = new_node
                break
            current = current.right
    return root


def _inorder_iterative(root) -> list:
    """
    Recorrido inorden iterativo usando una pila explícita.
    Evita RecursionError en árboles muy profundos.
    """
    result  = []
    stack   = []
    current = root

    while current or stack:
        # Ir al nodo más a la izquierda
        while current:
            stack.append(current)
            current = current.left

        # Procesar el nodo
        current = stack.pop()
        result.append(current.data)

        # Moverse al subárbol derecho
        current = current.right

    return result


def tree_sort(data: list) -> list:
    root = None

    # Insertar todos los elementos iterativamente
    for item in data:
        root = _bst_insert_iterative(root, item)

    # Recorrido inorden iterativo
    return _inorder_iterative(root)
# ═══════════════════════════════════════════════════════
# 9. BUCKET SORT — O(n),  peor caso O(n²)
# Distribuye en cubetas y ordena cada una
# ═══════════════════════════════════════════════════════
def bucket_sort(data: list) -> list:
    if not data:
        return []

    arr = data[:]
    n   = len(arr)

    # Usamos el timestamp de la fecha como valor numérico
    # Convertimos fecha a número: YYYYMMDD → entero
    def date_to_int(record):
        return int(str(record["trade_date"]).replace("-", ""))

    min_val = date_to_int(min(arr, key=date_to_int))
    max_val = date_to_int(max(arr, key=date_to_int))

    # Creamos n cubetas
    buckets = [[] for _ in range(n)]

    # Distribuimos cada elemento en su cubeta
    for item in arr:
        val = date_to_int(item)
        if max_val == min_val:
            idx = 0
        else:
            idx = int((val - min_val) / (max_val - min_val) * (n - 1))
        buckets[idx].append(item)

    # Ordenamos cada cubeta con Insertion Sort
    result = []
    for bucket in buckets:
        if bucket:
            sorted_bucket = binary_insertion_sort(bucket)
            result.extend(sorted_bucket)

    return result


# ═══════════════════════════════════════════════════════
# 10. PIGEONHOLE SORT — O(n + k)
# Una casilla por valor posible (ideal para rangos pequeños)
# ═══════════════════════════════════════════════════════
def pigeonhole_sort(data: list) -> list:
    if not data:
        return []

    arr = data[:]

    # Convertimos fecha a entero YYYYMMDD
    def date_to_int(record):
        return int(str(record["trade_date"]).replace("-", ""))

    min_val = date_to_int(min(arr, key=date_to_int))
    max_val = date_to_int(max(arr, key=date_to_int))
    size    = max_val - min_val + 1

    # Creamos los casilleros (uno por valor posible)
    holes = [[] for _ in range(size)]

    # Colocamos cada elemento en su casillero
    for item in arr:
        idx = date_to_int(item) - min_val
        holes[idx].append(item)

    # Recogemos los elementos de los casilleros en orden
    result = []
    for hole in holes:
        if hole:
            # Si hay múltiples elementos en el mismo casillero
            # los ordenamos por precio de cierre
            hole_sorted = selection_sort(hole)
            result.extend(hole_sorted)

    return result


# ═══════════════════════════════════════════════════════
# 11. RADIX SORT — O(nk)
# Ordena dígito por dígito usando Counting Sort como base
# ═══════════════════════════════════════════════════════
def radix_sort(data: list) -> list:
    if not data:
        return []

    arr = data[:]

    def date_to_int(record):
        return int(str(record["trade_date"]).replace("-", ""))

    max_val = date_to_int(max(arr, key=date_to_int))

    # Procesamos cada dígito de menos significativo a más significativo
    exp = 1
    while max_val // exp > 0:
        arr = _counting_sort_by_digit(arr, exp)
        exp *= 10

    return arr


def _counting_sort_by_digit(arr: list, exp: int) -> list:
    """Counting Sort estable basado en un dígito específico."""
    n       = len(arr)
    output  = [None] * n
    count   = [0] * 10  # Dígitos 0-9

    def get_digit(record):
        val = int(str(record["trade_date"]).replace("-", ""))
        return (val // exp) % 10

    # Contar ocurrencias de cada dígito
    for item in arr:
        count[get_digit(item)] += 1

    # Acumular conteos
    for i in range(1, 10):
        count[i] += count[i - 1]

    # Construir el arreglo de salida (recorremos al revés para estabilidad)
    for i in range(n - 1, -1, -1):
        digit          = get_digit(arr[i])
        count[digit]  -= 1
        output[count[digit]] = arr[i]

    return output


# ═══════════════════════════════════════════════════════
# 12. BITONIC SORT — O(n log²n)
# Versión iterativa para evitar RecursionError
# ═══════════════════════════════════════════════════════
def bitonic_sort(data: list) -> list:
    arr = data[:]
    n   = len(arr)

    # Rellenamos hasta potencia de 2
    power = 1
    while power < n:
        power *= 2

    padding = power - n
    arr.extend([{"trade_date": "9999-12-31", "close_price": 999999999}] * padding)

    size = power

    # Iteramos sobre cada tamaño de bloque
    k = 2
    while k <= size:
        # Iteramos sobre cada subarreglo de tamaño k
        j = k // 2
        while j >= 1:
            for i in range(size):
                l = i ^ j  # XOR para encontrar el par
                if l > i:
                    # Determinamos si este bloque va ascendente o descendente
                    ascending = (i & k) == 0
                    if ascending == (compare(arr[i], arr[l]) > 0):
                        arr[i], arr[l] = arr[l], arr[i]
            j //= 2
        k *= 2

    return arr[:n]