document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form");
    const closeBtn = document.querySelector(".close-btn");
    const container = document.querySelector(".register-container");
    const messageArea = document.getElementById("message-area");
    const passwordInput = document.getElementById("password");
    const togglePassword = document.querySelector(".toggle-password");
    const isRegister = document.querySelector('button.register-btn')?.textContent?.toLowerCase().includes('registrar');

    // Cerrar el formulario con animación
    closeBtn?.addEventListener("click", () => {
        container.style.animation = "fadeOutUp 0.6s forwards";
        setTimeout(() => {
            container.style.display = "none";
        }, 600);
    });

    // Mostrar/ocultar contraseña
    togglePassword?.addEventListener("click", () => {
        if (passwordInput.type === "password") {
            passwordInput.type = "text";
            togglePassword.innerHTML = '<i class="fas fa-eye-slash"></i>';
        } else {
            passwordInput.type = "password";
            togglePassword.innerHTML = '<i class="fas fa-eye"></i>';
        }
    });

    // Validación y mensajes bonitos
    form?.addEventListener("submit", (e) => {
        e.preventDefault();
        const username = document.getElementById("username")?.value.trim();
        const password = passwordInput?.value;
        if (isRegister) {
            const email = document.getElementById("email")?.value.trim();
            const terms = document.getElementById("terms")?.checked;
            if (!username || !email || !password || !terms) {
                showMessage("Por favor completa todos los campos y acepta los términos.", "error");
                return;
            }
            showMessage("¡Registro exitoso! 🎉", "success");
            form.reset();
        } else {
            if (!username || !password) {
                showMessage("Por favor ingresa tu usuario y contraseña.", "error");
                return;
            }
            showMessage("¡Bienvenido!", "success");
            form.reset();
        }
    });

    function showMessage(msg, type) {
        if (!messageArea) return;
        messageArea.textContent = msg;
        messageArea.className = type;
        messageArea.style.opacity = 1;
        setTimeout(() => {
            messageArea.style.opacity = 0;
        }, 2500);
    }

    // Redirigir a register.html solo cuando se presione el enlace de registro
    const registerLink = document.querySelector('.login-link a');
    if (registerLink && registerLink.textContent.toLowerCase().includes('regístrate')) {
        registerLink.addEventListener('click', function(e) {
            e.preventDefault();
            window.location.href = 'register.html';
        });
    }
});

// Animación fadeOutUp para cerrar
const style = document.createElement('style');
style.innerHTML = `
@keyframes fadeOutUp {
  0% { opacity: 1; transform: translateY(0); }
  100% { opacity: 0; transform: translateY(-40px); }
}`;
document.head.appendChild(style);
