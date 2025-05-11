<script>
    import { Input, Button, Form, FormGroup, Label, Alert } from '@sveltestrap/sveltestrap';
    import Fa from 'svelte-fa';
    import { faEye, faEyeSlash, faUser, faKey, faEnvelope } from '@fortawesome/free-solid-svg-icons';
    import { API_BASE_URL } from '../../config.js';

    let username = "";
    let email = "";
    let password = "";
    let errorMessage = "";

    let isUsernameInvalid = false;
    let isEmailInvalid = false;
    let isPasswordInvalid = false;
    let showPassword = false; // Estado para alternar la visibilidad de la contraseña

    function togglePasswordVisibility() {
        showPassword = !showPassword;
    }

    async function register() {
        errorMessage = ""; // Resetear mensaje de error
        isUsernameInvalid = isEmailInvalid = isPasswordInvalid = false;

        if (!username) isUsernameInvalid = true;
        if (!email) isEmailInvalid = true;
        if (!password) isPasswordInvalid = true;

        if (!username || !email || !password) {
            errorMessage = "Todos los campos son obligatorios.";
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, email, password })
            });

            const data = await response.json();
            if (response.ok) {
                alert("Registro exitoso, ahora puedes iniciar sesión");
                window.location.href = "/login";
            } else {
                errorMessage = data.error || "Error en el registro.";
            }
        } catch (error) {
            errorMessage = "No se pudo conectar con el servidor.";
        }
    }
</script>

<main class="flex items-center justify-center px-4">
    <div class="max-w-md w-full bg-white rounded-lg shadow-lg p-6 sm:p-10 text-center">
        <h2 class="text-2xl font-semibold text-gray-700 mb-4">Registro</h2>

        {#if errorMessage}
            <div class="bg-red-200 text-red-700 p-3 rounded-md mb-2">{errorMessage}</div>
        {/if}

        <Form on:submit={register} class="space-y-4">
            <FormGroup>
                <Label for="username" class="flex items-center space-x-2 text-sm font-medium text-gray-600"><Fa icon={faUser} size="1x" secondaryOpacity={1} primaryColor="blue" secondaryColor="linen"/><span>Usuario</span></Label>
                <Input
                    type="text"
                    bind:value={username}
                    required
                    placeholder="Nombre de usuario"
                    class="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 shadow-sm focus:ring-2 focus:ring-blue-400 focus:border-blue-500 transition"
                    invalid={isUsernameInvalid}
                />
            </FormGroup>

            <FormGroup>
                <Label for="email" class="flex items-center space-x-2 text-sm font-medium text-gray-600"><Fa icon={faEnvelope} size="1x" secondaryOpacity={1} primaryColor="blue" secondaryColor="linen"/><span>Correo electrónico</span></Label>
                <Input
                    type="email"
                    bind:value={email}
                    required
                    placeholder="Correo electrónico"
                    class="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 shadow-sm focus:ring-2 focus:ring-blue-400 focus:border-blue-500 transition"
                    invalid={isEmailInvalid}
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
                        invalid={isPasswordInvalid}
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

            <Button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded-xl shadow-md transition-all">
                Registrarse
            </Button>
        </Form>

        <p class="mt-4 text-center text-sm text-gray-500">
            ¿Ya tienes cuenta? <a href="/login" class="text-blue-500 hover:underline">Inicia sesión aquí</a>
        </p>
    </div>
</main>
