import csv
import heapq
from collections import deque, defaultdict
import networkx as nx  # Importar networkx para manipular y dibujar grafos
import matplotlib.pyplot as plt  # Importar matplotlib para mostrar el grafo

# Cargar destinos y si requieren visa
def cargar_destinos(path):
    destinos = {}
    try:
        with open(path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                codigo = row.get("Codigo")
                requiere_visa_str = row.get("RequiereVisa")
                if not codigo or requiere_visa_str is None:
                    print(f"Advertencia: Fila incompleta o con columnas faltantes en '{path}', se omite: {row}")
                    continue
                requiere_visa = requiere_visa_str.strip().lower() == "sí"
                destinos[codigo] = requiere_visa
        return destinos
    except FileNotFoundError:
        print(f"Error: El archivo de destinos '{path}' no se encontró.")
        return None
    except KeyError as e:
        print(f"Error al leer el archivo de destinos: Falta la columna esperada '{e}'. Asegúrese de que las columnas sean 'Codigo' y 'RequiereVisa'.")
        return None

# Cargar grafo de vuelos
def cargar_tarifas(path):
    grafo = defaultdict(list)
    todos_los_aeropuertos = set() # Conjunto para almacenar todos los aeropuertos mencionados en las tarifas
    try:
        with open(path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                origen = row.get("Origen")
                destino = row.get("Destino")
                precio_str = row.get("Precio")

                if not origen or not destino or precio_str is None:
                    print(f"Advertencia: Fila incompleta o con columnas faltantes en '{path}', se omite: {row}")
                    continue

                try:
                    precio = float(precio_str)
                except ValueError:
                    print(f"Advertencia: Precio inválido '{precio_str}' para el vuelo {origen}-{destino} en '{path}'. Se ignorará esta tarifa.")
                    continue

                grafo[origen].append((destino, precio))
                grafo[destino].append((origen, precio))  # vuelos en ambos sentidos
                todos_los_aeropuertos.add(origen)
                todos_los_aeropuertos.add(destino)
        return grafo, todos_los_aeropuertos
    except FileNotFoundError:
        print(f"Error: El archivo de tarifas '{path}' no se encontró.")
        return None, None
    except KeyError as e:
        print(f"Error al leer el archivo de tarifas: Falta la columna esperada '{e}'. Asegúrese de que las columnas sean 'Origen', 'Destino' y 'Precio'.")
        return None, None

# Dijkstra para minimizar costo
def dijkstra(grafo, origen, destino, permitidos):
    # (costo_actual, nodo_actual, camino_acumulado)
    heap = [(0, origen, [])]
    costos_minimos = {origen: 0}
    caminos_previos = {origen: None}

    while heap:
        costo, nodo, _ = heapq.heappop(heap)

        if costo > costos_minimos.get(nodo, float('inf')):
            continue

        for vecino, peso in grafo[nodo]:
            if vecino not in permitidos:
                continue

            nuevo_costo = costo + peso
            if nuevo_costo < costos_minimos.get(vecino, float('inf')):
                costos_minimos[vecino] = nuevo_costo
                caminos_previos[vecino] = nodo
                heapq.heappush(heap, (nuevo_costo, vecino, [])) # El tercer elemento no es crítico aquí

    # Reconstruir el camino
    if destino in caminos_previos:
        ruta = []
        actual = destino
        while actual is not None:
            ruta.insert(0, actual)
            actual = caminos_previos[actual]
        return ruta, costos_minimos[destino]
    else:
        return None, float('inf')

# BFS para minimizar escalas
def bfs(grafo, origen, destino, permitidos):
    cola = deque([(origen, [origen])])
    visitados = {origen}

    while cola:
        nodo, camino = cola.popleft()
        if nodo == destino:
            return camino, len(camino) - 1
        for vecino, _ in grafo[nodo]:
            if vecino in permitidos and vecino not in visitados:
                visitados.add(vecino)
                cola.append((vecino, camino + [vecino]))
    return None, float('inf')

# Funcion para visualizar el grafo
def visualizar_grafo(grafo_data, todos_los_aeropuertos, destinos_info, ruta_resaltada=None, origen_elegido=None, destino_elegido=None):
    G = nx.Graph()

    # Añadir todos los aeropuertos como nodos
    for airport_code in todos_los_aeropuertos:
        G.add_node(airport_code)

    # Añadir aristas (vuelos) con sus pesos (precios)
    edge_labels = {}
    for origen, conexiones in grafo_data.items():
        for destino, precio in conexiones:
            # Asegurarse de añadir la arista solo una vez si el grafo es no dirigido
            if (origen, destino) not in G.edges() and (destino, origen) not in G.edges():
                G.add_edge(origen, destino, weight=precio)
                edge_labels[(origen, destino)] = f"${precio:.0f}" # Mostrar precio sin decimales si es entero

    # Definir colores para los nodos (verde para sin visa, rojo para con visa)
    node_colors = []
    for node in G.nodes():
        if destinos_info.get(node, False): # Si requiere visa
            node_colors.append('salmon') # Rojo claro para los que requieren visa
        else: # No requiere visa
            node_colors.append('lightgreen') # Verde claro para los que no requieren visa

    # Definir el layout del grafo
    pos = nx.spring_layout(G, k=0.8, iterations=50) # Ajustar k para dispersar nodos si es necesario

    plt.figure(figsize=(14, 10)) # Aumentar el tamaño de la figura para mejor visualización

    # Dibujar nodos
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=3000) # Aumentar node_size

    # Dibujar etiquetas de nodos
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')

    # Dibujar aristas
    nx.draw_networkx_edges(G, pos, edge_color='gray', width=1.0)

    # Dibujar etiquetas de aristas (precios)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, font_color='blue')

    # Resaltar la ruta encontrada si existe
    if ruta_resaltada and len(ruta_resaltada) > 1:
        path_edges = list(zip(ruta_resaltada, ruta_resaltada[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=3.0)
        
        # Resaltar nodos de origen y destino de la ruta
        if origen_elegido and destino_elegido:
            nx.draw_networkx_nodes(G, pos, nodelist=[origen_elegido], node_color='gold', node_size=4000, label='Origen')
            nx.draw_networkx_nodes(G, pos, nodelist=[destino_elegido], node_color='mediumorchid', node_size=4000, label='Destino')
            # Asegurarse de redibujar las etiquetas de estos nodos resaltados
            nx.draw_networkx_labels(G, pos, labels={origen_elegido: origen_elegido, destino_elegido: destino_elegido}, font_size=10, font_weight='bold', font_color='black')


    plt.title("Mapa de Vuelos de Metro Travel")
    plt.axis('off') # Ocultar los ejes
    plt.show()

# Interfaz principal
def main():
    destinos = cargar_destinos("destinos.csv")
    if destinos is None:
        return

    # Modificado: cargar_tarifas ahora devuelve el grafo y todos los_aeropuertos
    grafo, todos_los_aeropuertos_tarifas = cargar_tarifas("tarifas.csv")
    if grafo is None:
        return
    
    # Combinar todos los aeropuertos conocidos (de destinos y tarifas)
    todos_los_aeropuertos_conocidos = set(destinos.keys()).union(todos_los_aeropuertos_tarifas)

   #Validaciones de entrada
    while True:
        origen = input("Código del aeropuerto de origen: ").strip().upper()
        if origen not in destinos: # Verifica si el código existe en los destinos cargados
            print(f"⚠️ Error: El código de aeropuerto de origen '{origen}' no existe en nuestros registros. Por favor, intente de nuevo.")
        else:
            break
    
    while True:
        destino = input("Código del aeropuerto de destino: ").strip().upper()
        if destino not in destinos: # Verifica si el código existe en los destinos cargados
            print(f"⚠️ Error: El código de aeropuerto de destino '{destino}' no existe en nuestros registros. Por favor, intente de nuevo.")
        else:
            break
    
    # Asegurarse de que el origen y destino no sean el mismo
    if origen == destino:
        print("⚠️ El aeropuerto de origen y el de destino no pueden ser el mismo.")
        print("Por favor, ejecute el programa de nuevo si desea buscar un viaje válido.")
        return

    while True:
        respuesta = input("¿Tiene visa? (sí/no): ").strip().lower()
        if respuesta in {"sí", "si", "s", "no", "n", "yes"}:
            tiene_visa = respuesta in {"sí", "si", "s", "yes"}
            break
        else:
            print("⚠️ Respuesta inválida. Por favor, responda 'sí' o 'no'.")
            
    while True:
        criterio = input("¿Minimizar costo o escalas? (costo/escalas): ").strip().lower()
        if criterio in {"costo", "escalas"}:
            break
        else:
            print("⚠️ Criterio no reconocido. Por favor, use 'costo' o 'escalas'.")

    # Filtrar nodos válidos basados en la visa
    permitidos = {k for k, v in destinos.items() if tiene_visa or not v}

    if destinos[origen] and not tiene_visa:
        print(f"⚠️ No se puede iniciar el viaje en '{origen}' porque requiere visa y usted no la posee.")
        # Visualizar el grafo de todas formas, pero sin ruta
        visualizar_grafo(grafo, todos_los_aeropuertos_conocidos, destinos)
        return
    if destinos[destino] and not tiene_visa:
        print(f"⚠️ No se puede terminar el viaje en '{destino}' porque requiere visa y usted no la posee.")
        # Visualizar el grafo de todas formas, pero sin ruta
        visualizar_grafo(grafo, todos_los_aeropuertos_conocidos, destinos)
        return
        
    ruta_encontrada = None # Variable para almacenar la ruta si se encuentra

    if criterio == "costo":
        ruta, total = dijkstra(grafo, origen, destino, permitidos)
        if ruta:
            print(f"Ruta más barata: {' -> '.join(ruta)} (Costo Total: ${total:.2f})")
            ruta_encontrada = ruta
        else:
            print("No hay ruta disponible para el costo especificado.")
    elif criterio == "escalas":
        ruta, total = bfs(grafo, origen, destino, permitidos)
        if ruta:
            print(f"Ruta con menos escalas: {' -> '.join(ruta)} (Total de escalas: {total})")
            ruta_encontrada = ruta
        else:
            print("No hay ruta disponible para el número de escalas especificado.")
    else:
        print("Error interno: Criterio de búsqueda inválido.") # Este else ya no debería ejecutarse

    # Visualizar el grafo al final
    visualizar_grafo(grafo, todos_los_aeropuertos_conocidos, destinos, ruta_encontrada, origen, destino)

if __name__ == "__main__":
    main()