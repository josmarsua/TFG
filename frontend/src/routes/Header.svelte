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
                        profilePicture = "/uploads/default_profile.webp";
                    }

                } catch (error) {
                    console.error("Error al obtener la imagen de perfil:", error);
                    profilePicture = "/uploads/default_profile.webp"; // Imagen por defecto en caso de error
                }
            } else {
                profilePicture = "/uploads/default_profile.webp"; // Si no está autenticado, usar la imagen por defecto
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

<header class="bg-blue-900 p-4 text-white">
    <div class="max-w-4xl mx-auto flex justify-between items-center">
        <!-- Logo / Título -->
        <div class="text-xl font-bold">
            <a href="/">TFG josmarsua</a>
        </div>

        <!-- Navegación -->
        <div class="space-x-4 flex items-center">
            {#if isAuthenticated}
                <!-- Botón de Analizar (Solo si está autenticado) -->
                <a href="/process" class="bg-blue-500 hover:bg-blue-700 font-semibold py-2 px-4 rounded">
                    Analizar
                </a>

                <!-- Icono de usuario con imagen de perfil -->
                <a href="/dashboard" class="flex items-center space-x-2 hover:opacity-80">
                    <img src={profilePicture} alt="Perfil" class="w-10 h-10 rounded-full border border-white shadow-md">
                </a>

                <!-- Botón de Cerrar Sesión -->
                <button 
                    on:click={logout}
                    class="bg-red-500 hover:bg-red-700 font-semibold py-1 px-2 rounded"
                >
                    <Fa icon={faPowerOff} size="1x" secondaryOpacity={1}/>
                </button>
            {:else}
                <!-- Botón de Iniciar Sesión / Registrarse -->
                <a href="/login" class="bg-yellow-300 hover:bg-yellow-50 text-black font-semibold py-2 px-4 rounded">
                    Iniciar sesión
                </a>
                <a href="/register" class="bg-violet-300 hover:bg-purple-400 text-black font-semibold py-2 px-4 rounded">
                    Registrarse
                </a>
            {/if}
        </div>
    </div>
</header>
