from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# Crear la aplicación Flask
app = Flask(__name__)

# Permitir solicitudes Cross-Origin Resource Sharing (CORS)
# Esto habilita que el frontend (que puede estar en otro origen)
# pueda hacer peticiones al backend sin problemas de política de mismo origen.
CORS(app)

# Ruta principal para mostrar la página HTML (index.html)
@app.route('/')
def home():
    # Renderiza y devuelve el archivo index.html ubicado en la carpeta "templates"
    return render_template('mapa.html')

# Lista estática que almacena los puntos de basura con sus datos:
# id único, latitud, longitud y si ha sido visitado o no.
puntos_basura = [
    {"id": 1, "lat": -12.2234081, "lon": -76.9597511, "visitado": False},
    {"id": 2, "lat": -12.2246028, "lon": -76.9305266, "visitado": False},
    {"id": 3, "lat": -12.2130049, "lon":-76.9483784, "visitado": False},


]

# Función para calcular la distancia Euclidiana simple entre dos puntos geográficos.
# Se usa para determinar qué punto está más cercano.
def distancia(lat1, lon1, lat2, lon2):
    # Raíz cuadrada de la suma de las diferencias al cuadrado (distancia 2D)
    return ((lat1 - lat2)**2 + (lon1 - lon2)**2)**0.5

# Ruta para obtener todos los puntos de basura en formato JSON
@app.route('/puntos')
def obtener_puntos():
    # Devuelve la lista completa de puntos con todos sus atributos
    return jsonify(puntos_basura)

# Ruta que recibe coordenadas (lat, lon) y devuelve el punto de basura
# no visitado que está más cercano a esas coordenadas.
@app.route('/punto-cercano', methods=['POST'])
def punto_cercano():
    data = request.json  # Obtiene los datos enviados en formato JSON
    lat = data.get('lat')  # Latitud enviada
    lon = data.get('lon')  # Longitud enviada

    # Filtra los puntos que NO hayan sido visitados
    no_visitados = [p for p in puntos_basura if not p['visitado']]

    # Si no hay puntos no visitados, retorna mensaje y código 404 (no encontrado)
    if not no_visitados:
        return jsonify({"mensaje": "No hay puntos no visitados"}), 404

    # Busca el punto no visitado más cercano usando la función de distancia
    cercano = min(no_visitados, key=lambda p: distancia(lat, lon, p['lat'], p['lon']))

    # Devuelve ese punto cercano en formato JSON
    return jsonify(cercano)

# Ruta para marcar un punto como visitado.
# Recibe el id del punto por la URL y usa método POST para modificar el estado.
@app.route('/marcar-visitado/<int:punto_id>', methods=['POST'])
def marcar_visitado(punto_id):
    # Recorre la lista de puntos para buscar el que tenga el id especificado
    for p in puntos_basura:
        if p['id'] == punto_id:
            # Cambia su atributo 'visitado' a True
            p['visitado'] = True
            # Devuelve mensaje de éxito en JSON
            return jsonify({"mensaje": f"Punto {punto_id} marcado como visitado"})

    # Si no encuentra el punto, devuelve un error 404 con mensaje
    return jsonify({"error": "Punto no encontrado"}), 404

# Ejecuta la aplicación en modo debug cuando se ejecuta este archivo directamente
if __name__ == '__main__':
    app.run(debug=True)
