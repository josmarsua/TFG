<script>
    import { Input, Button, Form, FormGroup, Label, Alert } from '@sveltestrap/sveltestrap';

    let username = "";
    let email = "";
    let password = "";
    let errorMessage = "";

    let isUsernameInvalid = false;
    let isEmailInvalid = false;
    let isPasswordInvalid = false;

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
            const response = await fetch("http://127.0.0.1:5000/auth/register", {
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
                <Label for="username" class="block text-sm font-medium text-gray-600">Usuario</Label>
                <Input
                    type="text"
                    bind:value={username}
                    required
                    placeholder="Nombre de usuario"
                    class="mt-1 w-full border rounded-lg px-3 py-2 shadow-sm transition"
                    invalid={isUsernameInvalid}
                />
            </FormGroup>

            <FormGroup>
                <Label for="email" class="block text-sm font-medium text-gray-600">Correo electrónico</Label>
                <Input
                    type="email"
                    bind:value={email}
                    required
                    placeholder="Correo electrónico"
                    class="mt-1 w-full border rounded-lg px-3 py-2 shadow-sm transition"
                    invalid={isEmailInvalid}
                />
            </FormGroup>

            <FormGroup>
                <Label for="password" class="block text-sm font-medium text-gray-600">Contraseña</Label>
                <Input
                    type="password"
                    bind:value={password}
                    required
                    placeholder="********"
                    class="mt-1 w-full border rounded-lg px-3 py-2 shadow-sm transition"
                    invalid={isPasswordInvalid}
                />
            </FormGroup>

            <Button type="submit" color="primary" class="w-full py-2 text-lg font-semibold rounded-lg shadow-md">
                Registrarse
            </Button>
        </Form>

        <p class="mt-4 text-center text-sm text-gray-500">
            ¿Ya tienes cuenta? <a href="/login" class="text-blue-500 hover:underline">Inicia sesión aquí</a>
        </p>
    </div>
</main>
