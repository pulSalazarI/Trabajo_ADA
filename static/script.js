// Inicializamos el mapa centrado en coordenadas dadas y zoom 14
const map = L.map('map').setView([-12.21321449000,-76.93709478000], 14);

// Añadimos la capa de mapa base de OpenStreetMap
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Crear icono personalizado para la personita
const iconoPersona = L.icon({
    iconUrl: '/static/images/icono_personita.png',  // Asegúrate que tu imagen esté en /static/images/
    iconSize: [32, 37],       // Tamaño del icono (ajústalo según tu imagen)
    iconAnchor: [16, 37],     // Punto de anclaje del icono (centro abajo)
    popupAnchor: [0, -37]     // Posición del popup respecto al icono
});

// Crear marcador de la personita en una posición inicial 
const marcadorPersona = L.marker([-12.2210067,-76.924343], {icon: iconoPersona})
    .addTo(map)
    .bindPopup('¡Aquí estás tú!');

// Objeto para guardar los marcadores, clave: id del punto
const markers = {};

// Función para cargar los puntos desde el backend y mostrarlos en el mapa
function cargarPuntos() {
    fetch('/puntos')
        .then(res => {
            if (!res.ok) {
                console.error('Error en la respuesta de /puntos:', res.status, res.statusText);
                return [];
            }
            return res.json();
        })
        .then(puntos => {
            console.log('Respuesta de /puntos:', puntos);
            if (!Array.isArray(puntos)) {
                console.error('La respuesta de /puntos no es un array:', puntos);
                return;
            }
            puntos.forEach(p => {
                if (typeof p.lat !== 'number' || typeof p.lon !== 'number') {
                    console.error('Punto inválido:', p);
                    return;
                }
                // Creamos marcador para cada punto
                const marker = L.marker([p.lat, p.lon]).addTo(map);
                // Guardamos el marcador en el objeto para poder eliminarlo después
                markers[p.id] = marker;
                // Asociamos popup con botón para marcar como visitado y detalle
                marker.bindPopup(`
                Punto ID: ${p.id} <br>
                Visitado: ${p.visitado} <br>
                <button onclick="console.log('Botón Marcar Visitado presionado para punto ${p.id}');marcarVisitado(${p.id})" disabled>Marcar Visitado</button><br>
                <button onclick="console.log('Botón Marcar Ruta presionado para punto ${p.id}');marcarRuta(${p.lat}, ${p.lon})">Marcar Ruta</button><br>
                <button onclick="console.log('Botón Detalle presionado para punto ${p.id}');cargarDetalleDirecto(${p.id})">Detalle</button>
                `);
            });
        })
        .catch(err => {
            console.error('Error al obtener los puntos:', err);
        });
}

// Función para marcar un punto como visitado (llama al backend)
// Función para marcar un punto como visitado (llama al backend)
function marcarVisitado(id) {
    fetch(`/marcar-visitado/${id}`, {
        method: 'POST'
    })
    .then(res => res.json())
    .then(data => {
        //alert(data.mensaje || data.error);

        if (!data.error) {
            // Eliminamos el marcador del mapa y del objeto
            if (markers[id]) {
                map.removeLayer(markers[id]);
                delete markers[id];
            }
            // Si hay una ruta dibujada, la eliminamos
            if (rutaActual) {
                map.removeLayer(rutaActual);
                rutaActual = null;
            }
        }
    });
}

// Función para mostrar la ruta entre dos puntos
let rutaActual = null;

function mostrarRuta(inicio, destino) {
    fetch(`/ruta?inicio=${inicio}&destino=${destino}`)
        .then(res => res.json())
        .then(data => {
            const coords = data.coordenadas;
            if (coords.length > 0) {
                if (rutaActual) map.removeLayer(rutaActual);  // Quita anterior
                rutaActual = L.polyline(coords, { color: 'blue' }).addTo(map);
                map.fitBounds(rutaActual.getBounds());
                // Marcadores de inicio y destino
                L.marker(coords[0], {icon: iconoPersona}).addTo(map).bindPopup("Inicio").openPopup();
                L.marker(coords[coords.length - 1]).addTo(map).bindPopup("Destino");
            } else {
                alert("No se pudo calcular la ruta");
            }
        });
}

// Función para trazar la ruta desde la personita hasta un punto de basura
function marcarRuta(destLat, destLon) {
    const inicioLat = -12.2210067;
    const inicioLon = -76.924343;
    fetch(`/ruta?inicio_lat=${inicioLat}&inicio_lon=${inicioLon}&destino_lat=${destLat}&destino_lon=${destLon}`)
        .then(res => res.json())
        .then(data => {
            const coords = data.coordenadas;
            if (coords && coords.length > 0) {
                if (rutaActual) map.removeLayer(rutaActual);
                rutaActual = L.polyline(coords, { color: 'blue' }).addTo(map);
                map.fitBounds(rutaActual.getBounds());
                // Deshabilitar todos los botones de "Marcar Ruta" y habilitar los de "Marcar Visitado"
                document.querySelectorAll('button').forEach(btn => {
                    if (btn.textContent === 'Marcar Ruta') {
                        btn.disabled = true;
                    }
                    if (btn.textContent === 'Marcar Visitado') {
                        btn.disabled = false;
                    }
                });
            } else {
                alert("No se pudo calcular la ruta");
            }
        });
}


// Nueva función para consumir la API directamente al presionar el botón Detalle
function cargarDetalleDirecto(id_p_basura) {
    fetch(`/puntos-basura-detalles?id_p_basura=${id_p_basura}`)
        .then(res => res.json())
        .then(data => {
            console.log('[DETALLE DIRECTO] Datos recibidos:', data);
            // Mostrar los datos directamente en el componente detalle_basura.html
            mostrarDetalleEnSidebar(data);
        })
        .catch(err => {
            console.error('[DETALLE DIRECTO] Error al consultar la API:', err);
        });
}

function mostrarDetalleEnSidebar(data) {
    // Cargar el HTML del componente detalle_basura.html en el sidebar
    fetch('/detalle_basura')
        .then(res => res.text())
        .then(html => {
            document.getElementById('detalleBasuraContent').innerHTML = html;
            setTimeout(() => {
                console.log('[DEBUG] Data recibido para llenar el detalle:', data);
                // Si data tiene user_name, recompensa, descripcion, imagenes directamente
                const punto = data.user_name ? data : (data.resultado && data.resultado[0] ? data.resultado[0] : null);
                if (punto) {
                    console.log('[DEBUG] Punto procesado para el detalle:', punto);
                    document.getElementById('detalle-titulo').textContent = 'Punto de basura';
                    document.getElementById('detalle-publicado-por').textContent = punto.user_name || punto.id_usuario || '';
                    document.getElementById('detalle-recompensa').textContent = punto.recompensa || '0.00';
                    document.getElementById('detalle-descripcion').textContent = punto.descripcion || '';
                    const galeria = document.getElementById('detalle-galeria');
                    galeria.innerHTML = '';
                    (punto.imagenes || []).forEach(url => {
                        const img = document.createElement('img');
                        img.src = url;
                        img.alt = 'Foto';
                        galeria.appendChild(img);
                    });
                } else {
                    console.warn('[DEBUG] No se encontró punto válido en la respuesta:', data);
                }
            }, 50);
        });
}

// Función global para cerrar el detalle del sidebar derecho
function cerrarDetalleBasura() {
    const detalle = document.querySelector('.detalle-basura-container');
    if (detalle && detalle.parentNode) {
        detalle.parentNode.innerHTML = '';
    }
    // Restaurar el mensaje con el mismo estilo negro y amarillo
    const mensaje = document.getElementById('mensaje-inicial-detalle');
    if (!mensaje) {
        const cont = document.getElementById('detalleBasuraContent');
        if (cont) {
            cont.innerHTML = `<div id=\"mensaje-inicial-detalle\" style=\"background: #000; color: #ffe066; font-size: 1.18rem; text-align: left; border-radius: 18px; padding: 32px 28px 28px 32px; max-width: 95%; box-shadow: 0 2px 12px rgba(0,0,0,0.18); font-family: 'Segoe UI', 'Arial', sans-serif; font-weight: 500; line-height: 1.7; border: 1.5px solid #ffe066; margin: 18px 0; letter-spacing: 0.01em;\">
                <span style=\"display: block; font-size: 1.35rem; font-weight: bold; color: #ffe066; margin-bottom: 18px; text-align: center; letter-spacing: 0.02em;\">¡Transforma tu tiempo en impacto!</span>
                <ol style=\"margin: 0 0 18px 18px; padding: 0; color: #ffe066;\">
                    <li>Selecciona un punto de basura en el mapa, sigue la ruta y recógela.</li>
                    <li>Por cada acción, ganas dinero y contribuyes a un mundo más limpio, seguro y saludable.</li>
                </ol>
                <span style=\"display: block; font-size: 1.08rem; color: #ffe066; text-align: center; margin-top: 10px; font-weight: 600;\">¡Tú ayudas al planeta y el planeta te lo agradece!</span>
            </div>`;
        }
    }
}

// Cargar los puntos cuando se carga el script
cargarPuntos();
