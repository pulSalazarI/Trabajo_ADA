from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from grafo.grafo_utils import construir_grafo_villa_el_salvador
from grafo.ruta import calcular_ruta

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('mapa.html')

# Lista de puntos de basura
puntos_basura = [
    {"id": 1, "lat": -12.2234081, "lon": -76.9597511, "visitado": False},
    {"id": 2, "lat": -12.2246028, "lon": -76.9305266, "visitado": False},
    {"id": 3, "lat": -12.2130049, "lon": -76.9483784, "visitado": False},
]

def distancia(lat1, lon1, lat2, lon2):
    return ((lat1 - lat2)**2 + (lon1 - lon2)**2)**0.5

@app.route('/puntos')
def obtener_puntos():
    return jsonify(puntos_basura)

@app.route('/punto-cercano', methods=['POST'])
def punto_cercano():
    data = request.json
    lat = data.get('lat')   #comentario
    lon = data.get('lon')

    no_visitados = [p for p in puntos_basura if not p['visitado']]
    if not no_visitados:
        return jsonify({"mensaje": "No hay puntos no visitados"}), 404

    cercano = min(no_visitados, key=lambda p: distancia(lat, lon, p['lat'], p['lon']))
    return jsonify(cercano)

@app.route('/marcar-visitado/<int:punto_id>', methods=['POST'])
def marcar_visitado(punto_id):
    for p in puntos_basura:
        if p['id'] == punto_id:
            p['visitado'] = True
            return jsonify({"mensaje": f"Punto {punto_id} marcado como visitado"})
    return jsonify({"error": "Punto no encontrado"}), 404

# Construcción del grafo desde CSV
grafo, coordenadas = construir_grafo_villa_el_salvador("grafo/lista_adyacencia_completa.csv")

# Función para encontrar el nodo más cercano dadas unas coordenadas
def encontrar_nodo_mas_cercano(coord, coordenadas):
    lat0, lon0 = coord
    return min(
        coordenadas.items(),
        key=lambda item: (lat0 - item[1][0])**2 + (lon0 - item[1][1])**2
    )[0]

@app.route('/ruta')
def obtener_ruta():
    try:
        inicio_lat = float(request.args.get('inicio_lat'))
        inicio_lon = float(request.args.get('inicio_lon'))
        destino_lat = float(request.args.get('destino_lat'))
        destino_lon = float(request.args.get('destino_lon'))

        # Buscar nodos más cercanos en el grafo
        nodo_inicio = encontrar_nodo_mas_cercano((inicio_lat, inicio_lon), coordenadas)
        nodo_destino = encontrar_nodo_mas_cercano((destino_lat, destino_lon), coordenadas)

        # Calcular la ruta
        camino, _ = calcular_ruta(grafo, nodo_inicio, nodo_destino)

        # Convertir nodos a coordenadas (lat, lon)
        coords = [coordenadas[str(n)] for n in camino if str(n) in coordenadas]
        return jsonify({"coordenadas": coords})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
