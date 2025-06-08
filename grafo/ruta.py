import heapq

def dijkstra(grafo, inicio):
    distancias = {nodo: float('inf') for nodo in grafo}
    distancias[inicio] = 0
    anteriores = {nodo: None for nodo in grafo}
    heap = [(0, inicio)]

    while heap:
        distancia_actual, actual = heapq.heappop(heap)

        for vecino, peso in grafo.get(actual, []):
            nueva_distancia = distancia_actual + peso
            if nueva_distancia < distancias.get(vecino, float('inf')):
                distancias[vecino] = nueva_distancia
                anteriores[vecino] = actual
                heapq.heappush(heap, (nueva_distancia, vecino))

    return distancias, anteriores


def reconstruir_camino(anteriores, inicio, destino):
    camino = []
    actual = destino
    while actual is not None:
        camino.insert(0, actual)
        actual = anteriores.get(actual)
    if camino[0] == inicio:
        return camino
    return []


def calcular_ruta(grafo, inicio, destino):
    distancias, anteriores = dijkstra(grafo, inicio)
    camino = reconstruir_camino(anteriores, inicio, destino)
    return camino, distancias.get(destino, float('inf'))
