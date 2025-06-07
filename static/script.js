
// Inicializamos el mapa centrado en coordenadas dadas y zoom 14
const map = L.map('map').setView([-12.0464, -77.0428], 14);

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

// Crear marcador de la personita en una posición inicial (ejemplo)
const marcadorPersona = L.marker([-12.0465, -77.0425], {icon: iconoPersona})
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

                // Asociamos popup con botón para marcar como visitado
                marker.bindPopup(`
                    Punto ID: ${p.id} <br>
                    Visitado: ${p.visitado} <br>
                    <button onclick="marcarVisitado(${p.id})">Marcar Visitado</button>
                `);
            });
        });
}

// Función para marcar un punto como visitado (llama al backend)
function marcarVisitado(id) {
    fetch(`http://127.0.0.1:5000/marcar-visitado/${id}`, {
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
        }
    });
}

// Cargar los puntos cuando se carga el script
cargarPuntos();
