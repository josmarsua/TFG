<style>
    @import "/styles.css";
    @import url('https://fonts.googleapis.com/css2?family=Rubik:ital,wght@0,300..900;1,300..900&display=swap');

    .animate-progress {
        animation: progress 2s infinite;
    }

    @keyframes progress {
        0% {
            width: 0;
        }
        50% {
            width: 50%;
        }
        100% {
            width: 100%;
        }
    }
</style>

<svelte:head>
    <script src="https://cdn.tailwindcss.com"></script>
</svelte:head>

<script>
    import { Container, Row, Col, Card, Button, Input } from '@sveltestrap/sveltestrap';

    let file = null;
    let processedFile = null;
    let trajectoryFile = null;
    let processedPreviewURL = null;
    let trajectoryPreviewURL = null;

    let isLoading = false; // Estado para mostrar la barra de progreso

    async function uploadFile() {
        if (!file) {
            alert("Por favor, selecciona un archivo");
            return;
        }

        isLoading = true; // Mostrar barra de progreso

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch('http://127.0.0.1:5000/upload', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error("Error al procesar el archivo");
            }

            const data = await response.json();
            processedFile = `http://127.0.0.1:5000${data.processed_file}`;
            trajectoryFile = `http://127.0.0.1:5000${data.trajectory_file}`;
            // URLs para los videos
            processedPreviewURL = processedFile.replace('/download/', '/processed/');
            trajectoryPreviewURL = trajectoryFile.replace('/download/', '/processed/');
        } catch (error) {
            alert(error.message);
        } finally {
            isLoading = false; // Ocultar barra de progreso
        }
    }
    
</script>

<main>
    <div class="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
        <header class="text-center mb-8">
            <h1 class="text-3xl font-bold text-gray-800">Sube un vídeo</h1>
            <p class="text-lg text-gray-600">
                [descripción]
            </p>
        </header>
        <Container>
            <Row>
                <Col class="text-center">
                    <Input type="file" accept="video/*" on:change="{e => file = e.target.files[0]}" />
                </Col>
                <Col class="text-center">
                    <Button color="primary" on:click="{uploadFile}" disabled={isLoading}>
                        {isLoading ? "Procesando..." : "Subir"}
                    </Button>
                </Col>
            </Row>
        </Container>

        {#if isLoading}
            <!-- Barra de Progreso -->
            <div class="mt-4">
                <div class="w-full bg-gray-200 rounded-full h-4">
                    <div class="bg-blue-500 h-4 rounded-full animate-progress"></div>
                </div>
            </div>
        {/if}

        {#if processedFile && trajectoryFile}
            <div class="mt-8">
                <h2 class="text-2xl font-semibold text-gray-800">Resultados</h2>

                <!-- Descargas -->
                <div class="mt-4">
                    <p><a href="{processedFile}" download class="text-blue-500 underline">Descargar Video Procesado</a></p>
                    <p><a href="{trajectoryFile}" download class="text-blue-500 underline">Descargar Video de Trayectorias</a></p>
                </div>
                
                <h3 class="text-xl font-bold text-gray-800">Previsualización</h3>

                <!-- Video Procesado -->
                <div class="mt-4">
                    <h4 class="text-lg font-semibold text-gray-700">Video Procesado</h4>
                    <!-- svelte-ignore a11y_media_has_caption -->
                    <video controls class="w-full max-w-lg mx-auto rounded shadow-lg">
                        <source src="{processedPreviewURL}" type="video/mp4" />
                        Tu navegador no soporta la reproducción de videos.
                    </video>
                </div>

                <!-- Video de Trayectorias -->
                <div class="mt-4">
                    <h4 class="text-lg font-semibold text-gray-700">Video de Trayectorias</h4>
                    <!-- svelte-ignore a11y_media_has_caption -->
                    <video controls class="w-full max-w-lg mx-auto rounded shadow-lg">
                        <source src="{trajectoryPreviewURL}" type="video/mp4" />
                        Tu navegador no soporta la reproducción de videos.
                    </video>
                </div>
            </div>
        {/if}
    </div>
</main>
