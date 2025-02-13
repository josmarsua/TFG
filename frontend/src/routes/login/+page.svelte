<script>
    import { authToken } from "../../store.js";
    import { Input, Button, Form, FormGroup, Label, Alert, Container, Row, Col } from '@sveltestrap/sveltestrap';
    import Fa from 'svelte-fa';
    import { faEye, faEyeSlash, faUser, faKey } from '@fortawesome/free-solid-svg-icons';

    let username = "";
    let password = "";
    let errorMessage = "";
    let usernameError = false;
    let passwordError = false;
    let showPassword = false; // Estado para alternar la visibilidad de la contraseña

    function togglePasswordVisibility() {
        showPassword = !showPassword;
    }

    async function login() {
        errorMessage = "";  // Resetear error antes de cada intento
        usernameError = false;
        passwordError = false;

        if (!username || !password) {
            errorMessage = "Por favor, introduce usuario y contraseña.";
            usernameError = !username;
            passwordError = !password;
            return;
        }

        try {
            const response = await fetch("http://127.0.0.1:5000/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();
            if (response.ok) {
                authToken.set(data.token);
                window.location.href = "/dashboard";  // Redirigir tras login
            } else {
                errorMessage = String(data.error || "Error en el inicio de sesión.");
                usernameError = true;
                passwordError = true;
            }
        } catch (error) {
            errorMessage = "No se pudo conectar con el servidor.";
        }
    }

    import { fade } from 'svelte/transition';
</script>

<main class="flex items-center justify-center px-4 sm:px-6">
    <div class="max-w-md w-full bg-white rounded-lg shadow-lg p-6 sm:p-10">
        <h2 class="text-2xl font-semibold text-center text-gray-700">Iniciar sesión</h2>

        {#if errorMessage}
            <div class="bg-red-200 text-red-700 p-3 rounded-md mb-2 flex justify-between items-center" transition:fade>
                <span>{errorMessage}</span>
                <button
                    class="ml-4 px-2 py-1 text-red-900 font-bold bg-red-300 hover:bg-red-400 rounded-full"
                    on:click={() => errorMessage = ""}
                >
                    ×
                </button>
            </div>
        {/if}

        <Form on:submit={login} class="space-y-4">
            <FormGroup>
                <Label for="username" class="flex items-center space-x-2 text-sm font-medium text-gray-600"><Fa icon={faUser} size="1x" secondaryOpacity={1} primaryColor="blue" secondaryColor="linen"/><span>Usuario</span></Label>
                <Input
                    type="text"
                    bind:value={username}
                    required
                    placeholder="Nombre de usuario"
                    invalid={usernameError}
                    class="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 shadow-sm focus:ring-2 focus:ring-blue-400 focus:border-blue-500 transition"
                />
            </FormGroup>

            <FormGroup>
                <Label for="password" class="flex items-center space-x-2 text-sm font-medium text-gray-600"><Fa icon={faKey} size="1x" secondaryOpacity={1} primaryColor="blue" secondaryColor="linen"/><span>Contraseña</span></Label>
                <div class="relative">
                    <Input
                        type={showPassword ? "text" : "password"}
                        bind:value={password}
                        required
                        placeholder="********"
                        invalid={passwordError}
                        class="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 shadow-sm focus:ring-2 focus:ring-blue-400 focus:border-blue-500 transition pr-10"
                    />
                    <Button 
                        type="button"
                        color="light"
                        class="absolute inset-y-0 right-0 px-3 flex items-center text-gray-600 hover:text-gray-900"
                        on:click={togglePasswordVisibility}
                    >
                        <Fa icon={showPassword ? faEyeSlash : faEye} />
                    </Button>
                </div>
            </FormGroup>

            <Button type="submit" color="primary" class="w-full py-2 text-lg font-semibold rounded-lg shadow-md">
                Iniciar sesión
            </Button>
        </Form>

        <p class="mt-4 text-center text-sm text-gray-500">
            ¿No tienes cuenta? <a href="/register" class="text-blue-500 hover:underline">Regístrate aquí</a>
        </p>
    </div>
</main>

