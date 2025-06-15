from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from grafo.grafo_utils import construir_grafo_villa_el_salvador
from grafo.ruta import calcular_ruta
from dotenv import load_dotenv
import os
import requests

app = Flask(__name__)
CORS(app)

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


@app.route('/mapa')
def home():
    return render_template('mapa.html')

@app.route('/')
def bienvenida():
    return render_template('Bienvenida.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/detalle_basura')
def detalle_basura():
    return render_template('detalle_basura.html')



#BACKEND

# Función para obtener puntos de basura desde Supabase
import requests

def obtener_puntos_supabase():
    url = f"{SUPABASE_URL}/rest/v1/p_basura?select=id_p_basura,latitud,longitud,estado_activo&estado_activo=eq.1"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        datos = response.json()
        return [
            {
                "id": p["id_p_basura"],
                "lat": float(p["latitud"]),
                "lon": float(p["longitud"]),
                "visitado": False
            }
            for p in datos
        ]
    else:
        print("Error al obtener datos:", response.status_code, response.text)
        return []

@app.route('/puntos')
def obtener_puntos():
    return jsonify(obtener_puntos_supabase())


@app.route('/marcar-visitado/<int:punto_id>', methods=['POST'])
def marcar_visitado(punto_id):
    datos = request.get_json()
    id_recolector = datos.get("id_recolector")

    if not id_recolector:
        return jsonify({"error": "Falta id_recolector en la solicitud"}), 400

    url = f"{SUPABASE_URL}/rest/v1/p_basura?id_p_basura=eq.{punto_id}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "estado_activo": 0,
        "id_recolector": id_recolector
    }

    response = requests.patch(url, headers=headers, json=data)
    if response.status_code in [200, 204]:
        return jsonify({"mensaje": f"Punto {punto_id} marcado como visitado"})
    else:
        return jsonify({"error": "No se pudo actualizar el estado en Supabase"}), 400

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

        # Calcular la ruta se aplica djastra
        camino, _ = calcular_ruta(grafo, nodo_inicio, nodo_destino)

        # Convertir nodos a coordenadas (lat, lon)
        coords = [coordenadas[str(n)] for n in camino if str(n) in coordenadas]
        return jsonify({"coordenadas": coords})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
