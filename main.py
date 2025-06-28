import csv
import heapq
from collections import deque, defaultdict

# Cargar destinos y si requieren visa
def cargar_destinos(path):
    destinos = {}
    with open(path, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            requiere_visa = row["RequiereVisa"].strip().lower() == "sí"
            destinos[row["Codigo"]] = requiere_visa
    return destinos

# Cargar grafo de vuelos
def cargar_tarifas(path):
    grafo = defaultdict(list)
    with open(path, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            origen = row["Origen"]
            destino = row["Destino"]
            precio = float(row["Precio"])
            grafo[origen].append((destino, precio))
            grafo[destino].append((origen, precio))  # vuelos en ambos sentidos
    return grafo

# Dijkstra para minimizar costo
def dijkstra(grafo, origen, destino, permitidos):
    heap = [(0, origen, [])]
    visitados = set()

    while heap:
        costo, nodo, camino = heapq.heappop(heap)
        if nodo in visitados:
            continue
        visitados.add(nodo)
        camino = camino + [nodo]
        if nodo == destino:
            return camino, costo
        for vecino, peso in grafo[nodo]:
            if vecino in permitidos:
                heapq.heappush(heap, (costo + peso, vecino, camino))
    return None, float('inf')

# BFS para minimizar escalas
def bfs(grafo, origen, destino, permitidos):
    cola = deque([(origen, [origen])])
    visitados = set()

    while cola:
        nodo, camino = cola.popleft()
        if nodo == destino:
            return camino, len(camino) - 1
        for vecino, _ in grafo[nodo]:
            if vecino in permitidos and vecino not in visitados:
                visitados.add(vecino)
                cola.append((vecino, camino + [vecino]))
    return None, float('inf')

# Interfaz principal
def main():
    destinos = cargar_destinos("destinos.csv")
    grafo = cargar_tarifas("tarifas.csv")

    origen = input("Código del aeropuerto de origen: ").strip().upper()
    destino = input("Código del aeropuerto de destino: ").strip().upper()

    respuesta = input("¿Tiene visa? (sí/no): ").strip().lower()
    tiene_visa = respuesta in {"sí", "si", "s", "yes"}

    criterio = input("¿Minimizar costo o escalas? (costo/escalas): ").strip().lower()

    # Filtrar nodos válidos
    permitidos = {k for k, v in destinos.items() if tiene_visa or not v}

    if origen not in permitidos or destino not in permitidos:
        print("⚠️ No se puede iniciar o terminar el viaje por restricciones de visa.")
        return

    if criterio == "costo":
        ruta, total = dijkstra(grafo, origen, destino, permitidos)
        if ruta:
            print(f"Ruta más barata: {' -> '.join(ruta)} (Costo: ${total:.2f})")
        else:
            print("No hay ruta disponible.")
    elif criterio == "escalas":
        ruta, total = bfs(grafo, origen, destino, permitidos)
        if ruta:
            print(f"Ruta con menos escalas: {' -> '.join(ruta)} (Escalas: {total})")
        else:
            print("No hay ruta disponible.")
    else:
        print("Criterio no reconocido. Usa 'costo' o 'escalas'.")

if __name__ == "__main__":
    main()
