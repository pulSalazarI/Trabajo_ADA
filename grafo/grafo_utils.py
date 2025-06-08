import csv

def construir_grafo_villa_el_salvador(path_csv):
    grafo = {}
    coordenadas = {}

    with open(path_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Saltar encabezado

        for row in reader:
            if not row or len(row) < 4:
                continue

            nodo = row[0]
            lat = float(row[1]) if row[1] else None
            lon = float(row[2]) if row[2] else None
            coordenadas[nodo] = (lat, lon)

            if nodo not in grafo:
                grafo[nodo] = []

            conexiones = row[3].split(',')
            for ady in conexiones:
                partes = ady.split(':')
                if len(partes) >= 2:
                    vecino = partes[0]
                    peso = float(partes[1])
                    grafo[nodo].append((vecino, peso))

    return grafo, coordenadas
