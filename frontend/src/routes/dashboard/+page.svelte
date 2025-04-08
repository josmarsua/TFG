<script>
    import { onMount } from "svelte";
    import { authToken } from "../../store.js";
    import { Button, Card, CardBody, CardTitle, CardText, Form, FormGroup, Label, Input, Container, Row, Col } from "@sveltestrap/sveltestrap";
    import Fa from 'svelte-fa';
    import { faEye, faEyeSlash, faUser, faKey, faEnvelope, faCamera } from '@fortawesome/free-solid-svg-icons';

    let user = { username: "", 
                    email: "", 
                    profile_picture: "" };
    let newUsername = "";
    let newEmail = "";
    let newPassword = "";
    let newProfilePicture = null;
    let errorMessage = "";
    let successMessage = "";

    async function fetchUserProfile() {
        try {
            const token = localStorage.getItem("token");
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
                user = data;
                newUsername = user.username;
                newEmail = user.email;
            } else {
                errorMessage = data.error || "Error al obtener perfil.";
            }
        } catch (error) {
            errorMessage = "Error al conectar con el servidor.";
        }
    }

    async function updateProfile() {
        successMessage = "";
        errorMessage = "";

        const formData = new FormData();
        formData.append("username", newUsername);
        formData.append("email", newEmail);
        if (newPassword) {
            formData.append("password", newPassword);
        }
        if (newProfilePicture) {
            formData.append("profile_picture", newProfilePicture);
        }

        try {
            const token = localStorage.getItem("token");
            const response = await fetch("http://127.0.0.1:5000/auth/update-profile", {
                method: "POST",
                headers: { Authorization: `Bearer ${token}` },
                body: formData
            });

            const data = await response.json();
            if (response.ok) {
                successMessage = data.message;
                user.username = newUsername;
                user.email = newEmail;
                user.profile_picture = `${data.profile_picture}?t=${new Date().getTime()}`;
                window.location.reload();
            } else {
                errorMessage = data.error;
            }
        } catch (error) {
            errorMessage = "Error al actualizar perfil.";
        }
    }

    function logout() {
        authToken.set(""); 
        localStorage.removeItem("token"); 
        window.location.href = "/login";
    }

    onMount(() => {
        fetchUserProfile();
    });
</script>
<div class="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
<Container>
    <Row class="w-100">
        <Col md="16" class="mx-auto">
            <Card class="shadow-lg">
                <CardBody class="text-center">
                    <h2 class="text-2xl font-semibold text-gray-700 mb-4">Perfil de usuario</h2>
                        {#if errorMessage}
                        <div class="alert alert-danger">{errorMessage}</div>
                        {/if}
                        <div class="flex align-items-center flex-column">
                            <img src={`http://127.0.0.1:5000/uploads/${user.profile_picture}`} alt="Foto de perfil" class="rounded-circle border border-gray-300 shadow-sm" width="100">                            
                            <h2 class="fw-bold text-center">{user.username}</h2>
                        </div>
                        
                    
                        <Form on:submit={updateProfile}>
                            <FormGroup>
                                <Label for="username" class="flex items-center space-x-2 text-sm font-medium text-gray-600"><Fa icon={faUser} size="1x" secondaryOpacity={1} primaryColor="blue" secondaryColor="linen"/><span>Usuario</span></Label>
                                <Input type="text" bind:value={newUsername} required />
                            </FormGroup>

                            <FormGroup>
                                <Label for="email" class="flex items-center space-x-2 text-sm font-medium text-gray-600"><Fa icon={faEnvelope} size="1x" secondaryOpacity={1} primaryColor="blue" secondaryColor="linen"/><span>Correo electrónico</span></Label>
                                <Input type="email" bind:value={newEmail} required />
                            </FormGroup>

                            <FormGroup>
                                <Label for="password" class="flex items-center space-x-2 text-sm font-medium text-gray-600"><Fa icon={faKey} size="1x" secondaryOpacity={1} primaryColor="blue" secondaryColor="linen"/><span>Nueva contraseña</span></Label>
                                <Input type="password" bind:value={newPassword} placeholder="Dejar en blanco para no cambiar" />
                            </FormGroup>

                            <FormGroup>
                                <Label for="profile_picture" class="flex items-center space-x-2 text-sm font-medium text-gray-600"><Fa icon={faCamera} size="1x" secondaryOpacity={1} primaryColor="blue" secondaryColor="linen"/><span>Foto de perfil</span></Label>
                                <Input type="file" accept="image/*" on:change="{e => newProfilePicture = e.target.files[0]}" />
                            </FormGroup>

                            {#if successMessage}
                                <div class="alert alert-success">{successMessage}</div>
                            {/if}

                            <Button type="submit" color="primary" class="w-100">Guardar Cambios</Button>
                        </Form>

                        <Button color="danger" class="w-100 mt-3" on:click={logout}>Cerrar sesión</Button>
                </CardBody>
            </Card>
        </Col>
    </Row>
</Container>
</div>
