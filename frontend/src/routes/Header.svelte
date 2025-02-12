<script>
    import { authToken } from "../store.js"; // Importamos el token de autenticación
    import { onMount } from "svelte";

    let isAuthenticated = false;

    // Verificar si el usuario está autenticado
    onMount(() => {
        authToken.subscribe(token => {
            isAuthenticated = !!token; // Si hay token, está autenticado
        });
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

                <!-- Botón de Cerrar Sesión -->
                <button 
                    on:click={logout}
                    class="bg-red-500 hover:bg-red-700 font-semibold py-2 px-4 rounded"
                >
                    Cerrar sesión
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
