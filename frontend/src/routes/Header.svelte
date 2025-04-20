<script>
    import { authToken } from "../store.js";
    import { onMount, onDestroy } from "svelte";
    import Fa from 'svelte-fa';
    import { faPowerOff } from '@fortawesome/free-solid-svg-icons';

    let isAuthenticated = false;
    let profilePicture = "http://127.0.0.1:5000/uploads/default_profile.webp"; // Imagen por defecto
    let unsubscribe; // Para manejar la suscripción y evitar múltiples llamadas

    // Verificar si el usuario está autenticado y obtener su imagen de perfil
    onMount(() => {
        // Obtener token de localStorage por si acaso
        let storedToken = localStorage.getItem("token");
        if (storedToken) {
            authToken.set(storedToken);
        }

        // Suscripción a cambios en el token de autenticación
        unsubscribe = authToken.subscribe(async (token) => {
            isAuthenticated = !!token;
            if (isAuthenticated) {
                try {
                    const response = await fetch("http://127.0.0.1:5000/auth/profile", {
                        method: "GET",
                        headers: { "Authorization": `Bearer ${token}` },
                    });

                    if (!response.ok) throw new Error("Error en la respuesta del servidor");

                    const data = await response.json();
                    if (data.profile_picture) {
                        profilePicture = `http://127.0.0.1:5000/uploads/${data.profile_picture}`;
                    } else {
                        profilePicture = "/default_profile.webp";
                    }

                } catch (error) {
                    console.error("Error al obtener la imagen de perfil:", error);
                    profilePicture = "/default_profile.webp"; // Imagen por defecto en caso de error
                }
            } else {
                profilePicture = "/default_profile.webp"; // Si no está autenticado, usar la imagen por defecto
            }
        });
    });

    // Desuscribirse cuando el componente se destruye para evitar múltiples suscripciones
    onDestroy(() => {
        if (unsubscribe) unsubscribe();
    });

    function logout() {
        authToken.set(""); // Eliminar token
        localStorage.removeItem("token"); // Borrar del almacenamiento
        window.location.href = "/"; // Redirigir a la página de inicio
    }
</script>

<svelte:head>
    <script src="https://cdn.tailwindcss.com"></script>
</svelte:head>

<header class="bg-[#0A0F2C] p-4 text-white shadow-md">
    <div class="max-w-4xl mx-auto flex justify-between items-center">
        <!-- Logo / Título -->
        <a href="/" class="flex items-center space-x-3">
            <img src="/logo.png" class="w-10 h-10" alt="Logo" />
            <span class="text-2xl font-semibold tracking-tight">Basket<span class="text-cyan-300">Vision</span></span>
        </a>
          

        <!-- Navegación -->
        <div class="space-x-4 flex items-center">
            {#if isAuthenticated}
                <!-- Botón de Analizar (Solo si está autenticado) -->
                <a href="/process"
                   class="bg-cyan-500 hover:bg-cyan-600 text-white font-semibold py-2 px-5 rounded-full shadow transition duration-200">
                    Analizar
                </a>


                <!-- Icono de usuario con imagen de perfil -->
                <a href="/dashboard" class="flex items-center space-x-2 hover:opacity-80">
                    <img src={profilePicture} alt="Perfil" class="w-10 h-10 rounded-full border-2 border-white shadow" />
                </a>

                <!-- Botón de Cerrar Sesión -->
                <button
                    on:click={logout}
                    class="bg-red-500 hover:bg-red-600 text-white rounded-full p-2 transition">
                    <Fa icon={faPowerOff} />
                </button>
            {:else}
                <!-- Botón de Iniciar Sesión / Registrarse -->
                <a href="/login" class="bg-yellow-400 hover:bg-yellow-300 text-black font-semibold py-2 px-4 rounded-full transition">
                    Iniciar sesión
                </a>
                <a href="/register" class="bg-violet-400 hover:bg-violet-500 text-white font-semibold py-2 px-4 rounded-full transition">
                    Registrarse
                </a>
            {/if}
        </div>
    </div>
</header>
