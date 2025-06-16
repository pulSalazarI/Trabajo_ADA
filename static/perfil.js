document.addEventListener('DOMContentLoaded', function() {
    // Obtener el nombre de usuario autenticado desde sessionStorage
    const userName = sessionStorage.getItem('usuario');
    if (!userName) return;

    // Consumir la API de perfil
    fetch(`/perfil-usuario?user_name=${encodeURIComponent(userName)}`)
        .then(res => res.json())
        .then(data => {
            if (data && !data.error) {
                // Si la API retorna el usuario directamente
                const usuario = data;
                // Si la API retorna {usuario: {...}}
                // const usuario = data.usuario || data;
                document.getElementById('nombre-usuario').textContent = usuario.nombres || '';
                document.getElementById('honor-barra').style.width = (usuario.honor || 0) + '%';
                document.getElementById('honor-texto').textContent = (usuario.honor || 0) + '%';
                document.getElementById('saldo').textContent = usuario.saldo !== undefined ? usuario.saldo : '';
                document.getElementById('correo').textContent = usuario.correo || '';
                document.getElementById('total-puntos').textContent = usuario.total_puntos_recolectados !== undefined ? usuario.total_puntos_recolectados : '';
            }
        });

    document.getElementById('btn-publicar').addEventListener('click', function() {
        window.location.href = '/publicar';
    });
});