<script>
    import { onMount } from "svelte";
    import { authToken } from "../../store.js";
    import { Button, Card, CardBody, CardTitle, CardText } from "@sveltestrap/sveltestrap";

    let user = { username: "", email: "" };
    let errorMessage = "";

    async function fetchUserProfile() {
        try {
            const token = $authToken;
            if (!token) {
                errorMessage = "No tienes acceso. Inicia sesión primero.";
                return;
            }

            const response = await fetch("http://127.0.0.1:5000/auth/profile", {
                method: "GET",
                headers: { Authorization: `Bearer ${token}` },
            });

            const data = await response.json();
            if (response.ok) {
                user = { username: data.username, email: data.email };
            } else {
                errorMessage = data.error || "Error al obtener perfil.";
            }
        } catch (error) {
            errorMessage = "Error al conectar con el servidor.";
        }
    }

    function logout() {
        authToken.set(""); // Eliminar token
        window.location.href = "/login"; // Redirigir al login
    }

    onMount(() => {
        fetchUserProfile();
    });
</script>

<main class="flex items-center justify-center px-4">
    <div class="max-w-md w-full bg-white rounded-lg shadow-lg p-6 sm:p-10 text-center">
        <h2 class="text-2xl font-semibold text-gray-700 mb-4">Perfil de usuario</h2>

        {#if errorMessage}
            <div class="bg-red-200 text-red-700 p-3 rounded-md mb-2">{errorMessage}</div>
        {:else}
            <Card class="mb-4">
                <CardBody>
                    <CardTitle class="text-xl font-bold">{user.username}</CardTitle>
                    <CardText class="text-gray-600">{user.email}</CardText>
                </CardBody>
            </Card>
            <Button color="danger" class="w-full py-2" on:click={logout}>Cerrar sesión</Button>
        {/if}
    </div>
</main>
