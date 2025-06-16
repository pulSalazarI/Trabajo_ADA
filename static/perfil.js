document.addEventListener('DOMContentLoaded', function() {
    // Datos del usuario (simulados o desde API)
    const usuario = {
        nombres: "Raquel Sánchez",
        usuario: "RaquelS",
        honor: 85, // Porcentaje (0-100)
        calificacion: 4.7,
        saldo: 1850.75,
        correo: "raquelS@gmail.com"
    };

    // Formateador de saldo
    const formatearSaldo = (saldo) => {
        return saldo.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
    };

    // Inyectar datos en el HTML
    document.getElementById('nombres').textContent = usuario.nombres;
    document.getElementById('usuario').textContent = usuario.usuario;
    document.getElementById('honor-barra').style.width = `${usuario.honor}%`;
    document.getElementById('honor-texto').textContent = `${usuario.honor}%`;
    document.getElementById('calificacion').textContent = usuario.calificacion.toFixed(1);Add commentMore actions
    document.getElementById('saldo').textContent = formatearSaldo(usuario.saldo);
    document.getElementById('correo').textContent = usuario.correo;
});