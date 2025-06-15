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
    fetch('http://127.0.0.1:5000/puntos')
        .then(res => res.json())
        .then(puntos => {
            puntos.forEach(p => {
                // Creamos marcador para cada punto
                const marker = L.marker([p.lat, p.lon]).addTo(map);
                // Guardamos el marcador en el objeto para poder eliminarlo después
                markers[p.id] = marker;
                // Asociamos popup con botón para marcar como visitado y detalle
                marker.bindPopup(`
                Punto ID: ${p.id} <br>
                Visitado: ${p.visitado} <br>
                <button onclick="marcarVisitado(${p.id})" disabled>Marcar Visitado</button><br>
                <button onclick="marcarRuta(${p.lat}, ${p.lon})">Marcar Ruta</button><br>
                <button onclick="window.location.href='/detalle_basura'">Detalle</button>
                `);
            });
        });
}

// Función para marcar un punto como visitado (llama al backend)
function marcarVisitado(id) {
    const idRecolector = 1; // ⚠️ Aquí pones el ID real del recolector (puede venir de login u otro valor dinámico)
    fetch(`http://127.0.0.1:5000/marcar-visitado/${id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id_recolector: idRecolector })
    })
    .then(res => res.json())
    .then(data => {
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
        } else {
            alert(data.error);
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

// Mostrar barra lateral con detalle
function mostrarDetalleSidebar() {
    const sidebar = document.getElementById('sidebar-detalle');
    const content = document.getElementById('sidebar-content');
    fetch('/static/ctn_p_basura.html')
        .then(res => res.text())
        .then(html => {
            content.innerHTML = html;
            sidebar.style.display = 'block';
        });
}
function cerrarSidebarDetalle() {
    document.getElementById('sidebar-detalle').style.display = 'none';
}

// Cargar los puntos cuando se carga el script
cargarPuntos();
