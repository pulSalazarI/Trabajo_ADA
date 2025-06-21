from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from grafo.grafo_utils import construir_grafo_villa_el_salvador
from grafo.ruta import calcular_ruta
import osmnx as ox
import requests
from dotenv import load_dotenv
import os
import csv
import random


from werkzeug.utils import secure_filename  # ✅ ESTA ES LA CLAVE

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = 'static/b_imagenes'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

@app.route('/')
def home():
    return render_template('Bienvenida.html')

@app.route('/publicar')
def publicar():
    return render_template('page_publicaion.html')

@app.route('/publicar/componente')
def publicar_componente():
    return render_template('ctn_publicaion.html')

@app.route('/mapa_basura')
def mapa_basura():
    return render_template('mapa_basura.html')

@app.route('/bienvenida')
def bienvenida():
    return render_template('Bienvenida.html')

@app.route('/detalle_basura')
def detalle_basura():
    return render_template('detalle_basura.html')
@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/base')
def base():
    return render_template('base.html')
########################################################################

@app.route('/publicar-punto', methods=['POST'])
def publicar_punto():
    try:
        datos = request.get_json()

        user_name = datos.get("user_name")
        lat = datos.get("latitud")
        lon = datos.get("longitud")
        recompensa = datos.get("recompensa", 0.0)
        descripcion = datos.get("descripcion", "")
        imagenes = datos.get("imagenes", [])

        # Validar entrada mínima
        if not all([user_name, lat, lon]):
            
            return jsonify({"error": "Faltan datos obligatorios"}), 400

        # Obtener id_usuario desde user_name
        url_usuario = f"{SUPABASE_URL}/rest/v1/usuarios?select=id_usuario&user_name=eq.{user_name}"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        response_usuario = requests.get(url_usuario, headers=headers)
        if response_usuario.status_code != 200 or not response_usuario.json():
            return jsonify({"error": "Usuario no encontrado"}), 404
        id_usuario = response_usuario.json()[0]["id_usuario"]

        # Insertar el punto de basura
        punto_data = {
            "id_usuario": id_usuario,
            "latitud": lat,
            "longitud": lon,
            "recompensa": recompensa,
            "descripcion": descripcion
        }
        url_basura = f"{SUPABASE_URL}/rest/v1/p_basura"
        response_punto = requests.post(url_basura, headers=headers, json=punto_data)
        if response_punto.status_code != 201:
            return jsonify({"error": "No se pudo crear el punto"}), 500
        id_p_basura = response_punto.json()[0]["id_p_basura"]

        # Insertar las imágenes
        for url in imagenes:
            imagen_data = {
                "id_p_basura": id_p_basura,
                "url": url
            }
            requests.post(f"{SUPABASE_URL}/rest/v1/imagen", headers=headers, json=imagen_data)

        return jsonify({"mensaje": "Punto de basura creado exitosamente", "id_p_basura": id_p_basura})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


#################################################################################
@app.route('/subir', methods=['POST'])
def subir_imagen():
    if 'imagen' not in request.files:
        return '', 400

    archivo = request.files['imagen']
    if archivo.filename == '':
        return '', 400

    filename = secure_filename(archivo.filename)
    ruta = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    archivo.save(ruta)

    IP_PUBLICA = 'http://3.16.130.202'  # Cambia por tu IP real o dominio
    url = f"{IP_PUBLICA}/static/b_imagenes/{filename}"

    return url  # Solo se devuelve la URL como texto plano
###########################################################################

@app.route('/recolectar-punto', methods=['POST'])
def recolectar_punto():
    datos = request.get_json()

    user_name = datos.get("user_name")
    user_name_recolector = datos.get("user_name_recolector")
    recompensa = float(datos.get("recompensa", 0))
    id_p_basura = datos.get("id_p_basura")

    if not all([user_name, user_name_recolector, id_p_basura]):
        return jsonify({"error": "Faltan datos requeridos"}), 400

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    # 🔎 Obtener ID y saldo del usuario
    url_user = f"{SUPABASE_URL}/rest/v1/usuarios?user_name=eq.{user_name}&select=id_usuario,saldo"
    response_user = requests.get(url_user, headers=headers)
    if response_user.status_code != 200 or not response_user.json():
        return jsonify({"error": "No se encontró al usuario"}), 404
    usuario_data = response_user.json()[0]
    id_usuario = usuario_data['id_usuario']
    saldo_usuario = float(usuario_data['saldo'])

    # 🔎 Obtener ID y saldo del recolector
    url_recolector = f"{SUPABASE_URL}/rest/v1/usuarios?user_name=eq.{user_name_recolector}&select=id_usuario,saldo"
    response_recolector = requests.get(url_recolector, headers=headers)
    if response_recolector.status_code != 200 or not response_recolector.json():
        return jsonify({"error": "No se encontró al recolector"}), 404
    recolector_data = response_recolector.json()[0]
    id_recolector = recolector_data['id_usuario']
    saldo_recolector = float(recolector_data['saldo'])

    # 🧾 Solo actualiza estado si no hay recompensa
    if recompensa == 0:
        patch_resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p_basura?id_p_basura=eq.{id_p_basura}",
            headers=headers,
            json={"id_recolector": id_recolector, "estado_activo": 0}
        )
        if patch_resp.status_code in [200, 204]:
            return jsonify({"mensaje": "Recojo registrado sin recompensa"}), 200
        else:
            return jsonify({"error": "Error al actualizar el estado"}), 500

    # 💰 Verificar si el usuario tiene saldo suficiente
    if saldo_usuario < recompensa:
        return jsonify({"error": "Saldo insuficiente para cubrir la recompensa"}), 400

    # 💵 Calcular comisión y ganancia
    comision = round(recompensa * 0.10, 2)
    ganancia_recolector = round(recompensa * 0.90, 2)
    nuevo_saldo_usuario = round(saldo_usuario - recompensa, 2)
    nuevo_saldo_recolector = round(saldo_recolector + ganancia_recolector, 2)

    # 💳 Actualizar saldo del publicador
    r1 = requests.patch(
        f"{SUPABASE_URL}/rest/v1/usuarios?id_usuario=eq.{id_usuario}",
        headers=headers,
        json={"saldo": nuevo_saldo_usuario}
    )
    if r1.status_code not in [200, 204]:
        return jsonify({"error": "Error al actualizar el saldo del usuario"}), 500

    # 💳 Actualizar saldo del recolector
    r2 = requests.patch(
        f"{SUPABASE_URL}/rest/v1/usuarios?id_usuario=eq.{id_recolector}",
        headers=headers,
        json={"saldo": nuevo_saldo_recolector}
    )
    if r2.status_code not in [200, 204]:
        return jsonify({"error": "Error al actualizar el saldo del recolector"}), 500

    # 📍 Actualizar estado del punto y asignar recolector
    r3 = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p_basura?id_p_basura=eq.{id_p_basura}",
        headers=headers,
        json={"id_recolector": id_recolector, "estado_activo": 0}
    )
    if r3.status_code not in [200, 204]:
        return jsonify({"error": "Error al actualizar el punto de basura"}), 500

    # 🧾 Registrar la comisión
    r4 = requests.post(
        f"{SUPABASE_URL}/rest/v1/comision",
        headers=headers,
        json={"id_p_basura": id_p_basura, "comision": comision}
    )
    if r4.status_code not in [200, 201]:
        return jsonify({"error": "Error al registrar la comisión"}), 500

    return jsonify({"mensaje": "Recompensa transferida exitosamente"}), 200


@app.route('/registrar-usuario', methods=['POST'])
def registrar_usuario():
    datos = request.get_json()
    
    # Validar campos requeridos
    campos_requeridos = ['nombres', 'user_name', 'correo', 'contrasena']
    if not all(campo in datos and datos[campo] for campo in campos_requeridos):
        return jsonify({'error': 'Faltan datos obligatorios'}), 400

    payload = {
        "nombres": datos['nombres'],
        "user_name": datos['user_name'],
        "correo": datos['correo'],
        "contrasena": datos['contrasena']
    }

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(f"{SUPABASE_URL}/rest/v1/usuarios", headers=headers, json=payload)

    if response.status_code in [200, 201]:
        
        return jsonify({"mensaje": "Usuario registrado correctamente"}), 201
    
    else:
        return jsonify({"error": "No se pudo registrar", "detalles": response.json()}), 500

@app.route('/perfil-usuario', methods=['GET'])
def obtener_perfil_usuario():
    user_name = request.args.get("user_name")
    if not user_name:
        return jsonify({'error': 'Falta el parámetro user_name'}), 400

    # Paso 1: Obtener datos del usuario
    url_usuario = f"{SUPABASE_URL}/rest/v1/usuarios?select=id_usuario,nombres,honor,saldo,correo&user_name=eq.{user_name}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    response_usuario = requests.get(url_usuario, headers=headers)
    if response_usuario.status_code != 200 or not response_usuario.json():
        return jsonify({'error': 'Usuario no encontrado'}), 404

    usuario = response_usuario.json()[0]
    id_usuario = usuario['id_usuario']

    # Paso 2: Contar puntos recolectados
    url_recolectados = f"{SUPABASE_URL}/rest/v1/p_basura?select=id_p_basura&select=count&and=(id_recolector.eq.{id_usuario},estado_activo.eq.0)"
    response_recolectados = requests.get(url_recolectados, headers=headers)

    total_puntos = 0
    if response_recolectados.status_code == 200 and isinstance(response_recolectados.json(), list):
        total_puntos = len(response_recolectados.json())

    # Armar resultado
    resultado = {
        'nombres': usuario['nombres'],
        'honor': usuario['honor'],
        'saldo': usuario['saldo'],
        'correo': usuario['correo'],
        'total_puntos_recolectados': total_puntos
    }

    return jsonify(resultado)



# Ruta para obtener usuarios desde Supabase
@app.route('/autentificacion', methods=['GET'])
def obtener_usuarios():
    url = f"{SUPABASE_URL}/rest/v1/usuarios?select=user_name,correo,contrasena"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'No se pudieron obtener los usuarios'}), 500

# Ruta para obtener puntos de basura desde Supabase


@app.route('/puntos-basura-detalles', methods=['GET'])
def detalle_punto_basura():
    id_p_basura = request.args.get("id_p_basura")
    if not id_p_basura:
        return jsonify({'error': 'Falta el parámetro id_p_basura'}), 400

    url = f"{SUPABASE_URL}/rest/v1/p_basura?select=id_p_basura,recompensa,descripcion,usuarios!p_basura_id_usuario_fkey(user_name),imagen(url)&id_p_basura=eq.{id_p_basura}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    print("[INFO] Solicitando datos a Supabase con URL:", url)
    response = requests.get(url, headers=headers)
    print("[INFO] Código de respuesta:", response.status_code)
    print("[INFO] Respuesta Supabase:", response.text)

    if response.status_code == 200:
        data = response.json()
        if not data:
            return jsonify({'error': 'No se encontró el punto de basura'}), 404

        punto = data[0]
        resultado = {
            'user_name': punto.get('usuarios', {}).get('user_name'),
            'recompensa': punto.get('recompensa'),
            'descripcion': punto.get('descripcion'),
            'imagenes': [img['url'] for img in punto.get('imagen', [])]
        }
        return jsonify(resultado)
    else:
        return jsonify({'error': 'Error al obtener los datos'}), 500





# Función para obtener puntos de basura desde Supabase
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
                "id": d["id_p_basura"],
                "lat": d["latitud"],
                "lon": d["longitud"],
                "visitado": d.get("visitado", False)
            }
            for d in datos
        ]
    else:
        return []

@app.route('/puntos')
def obtener_puntos():
    puntos = obtener_puntos_supabase()
    return jsonify(puntos)


@app.route('/marcar-visitado/<int:punto_id>', methods=['POST'])
def marcar_visitado(punto_id):
    url = f"{SUPABASE_URL}/rest/v1/p_basura?id_p_basura=eq.{punto_id}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    # Actualizar estado_activo a 0
    data = {"estado_activo": 0}
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code in [200, 204]:
        mensaje = f"Punto {punto_id} marcado como visitado"
        print(f"[INFO] {mensaje}")
        return jsonify({"mensaje": mensaje})
    else:
        print(f"[ERROR] No se pudo actualizar el punto {punto_id} en Supabase")
        return jsonify({"error": "No se pudo actualizar el estado en Supabase"}), 400
    

    # Construcción del grafo desde CSV
grafo, coordenadas = construir_grafo_villa_el_salvador("grafo/lista_adyacencia_completa.csv")


def encontrar_nodo_mas_cercano(coord, coordenadas):
    lat0, lon0 = coord
    return min(
        coordenadas.items(),
        key=lambda item: (lat0 - item[1][0])**2 + (lon0 - item[1][1])**2
    )[0]


def obtener_ubicacion():
    ruta_csv = r'grafo/lista_adyacencia_completa.csv'

    with open(ruta_csv, newline='', encoding='utf-8') as archivo:
        lector = csv.reader(archivo)
        next(lector)  # Saltar la cabecera

        filas = list(lector)
        fila_aleatoria = random.choice(filas)

        latitud = fila_aleatoria[1]
        longitud = fila_aleatoria[2]

        return latitud, longitud


# --- Ruta de cálculo de ruta entre dos nodos ---
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


@app.route('/simular-ubicacion', methods=['GET'])
def simular_ubicacion():
    lat, lon = obtener_ubicacion()
    return jsonify({'lat': lat, 'lon': lon})


if __name__ == '__main__':
    app.run(debug=True)
