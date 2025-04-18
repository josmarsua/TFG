<script>
    import { authToken } from "../../store.js";
    import { onMount } from "svelte";
    import { Container, Row, Col, Button, Input } from '@sveltestrap/sveltestrap';

    let file = null;
    let processedPreviewURL = null;
    let tempProcessedFile = ""; 
    let isAuthenticated = false;
    let isLoading = false;
    let errorMessage = "";
    let redirecting = false;

    let processingStatus = "";
    let videoId = "";
    let intervalId = null;

    let progress = 0;

    onMount(() => {
        authToken.subscribe(token => {
            isAuthenticated = !!token;
            if (!isAuthenticated) {
                redirecting = true;
                setTimeout(() => {
                    window.location.href = "/login";
                }, 8000);
            }
        });
    });

    async function uploadFile() {
        if (!file) {
            alert("Por favor, selecciona un archivo");
            return;
        }

        isLoading = true;
        processedPreviewURL = ""; 

        const formData = new FormData();
        formData.append("file", file);

        try {
            const token = localStorage.getItem("token");

            const response = await fetch('http://localhost:5000/video/upload', {
                method: 'POST',
                headers: {
                    "Authorization": `Bearer ${token}`
                },
                body: formData,
            });

            if (!response.ok) {
                throw new Error("Error al procesar el archivo");
            }

            const data = await response.json();
            videoId = data.video_id;
            tempProcessedFile = `http://localhost:5000${data.processed_file}`; 
            processingStatus = "🚀 Comenzando procesamiento...";

            intervalId = setInterval(pollStatus, 1000); // Poll every second

        } catch (error) {
            errorMessage = "Error al procesar el video. Asegúrate de estar autenticado.";
            isLoading = false;
        }
    }

    async function pollStatus() {
        try {
            const response = await fetch(`http://localhost:5000/video/status/${videoId}`);
            if (response.ok) {
                const data = await response.json();
                processingStatus = data.step;

                if (data.progress !== undefined) {
                    progress = data.progress;
                }

                if (processingStatus.includes("✅")) {
                    clearInterval(intervalId);
                    processedPreviewURL = tempProcessedFile; // <- MOSTRAR VIDEO
                }

                if (processingStatus.includes("❌")) {
                    clearInterval(intervalId);
                }
            }
        } catch (err) {
            console.error("Error haciendo polling:", err);
        }
    }

</script>

<svelte:head>
    <script src="https://cdn.tailwindcss.com"></script>
</svelte:head>
<main>
    {#if isAuthenticated}
        <div class="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
            <header class="text-center mb-8">
                <h1 class="text-3xl font-bold text-gray-800">Sube un vídeo</h1>
                <p class="text-lg text-gray-600">Selecciona un video para analizar.</p>
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
                <Row>
                    {#if processingStatus}
                        <Col class="text-center mt-4">
                            <div class="text-blue-600 font-medium animate-pulse">
                                {processingStatus}
                            </div>
                        </Col>
                    {/if}
                </Row>                
            </Container>

            {#if isLoading}
            <!-- Barra de Progreso -->
            <div class="mt-4">
                <div class="w-full bg-gray-200 rounded-full h-4">
                    <div class="bg-blue-500 h-4 rounded-full" style="width: {progress}%; transition: width 0.5s;"></div>
                </div>
                <p class="text-center text-sm text-gray-600 mt-1">{progress}%</p>
            </div>
            {/if}

            {#if processedPreviewURL}
                <div class="mt-8">
                    <h2 class="text-2xl font-semibold text-gray-800">Resultados</h2>
                    <div class="mt-4">
                        <!-- svelte-ignore a11y_media_has_caption -->
                        <video controls class="w-full max-w-lg mx-auto rounded shadow-lg">
                            <source src={processedPreviewURL} type="video/mp4" />
                            Tu navegador no soporta la reproducción de videos.
                        </video>
                    </div>
                </div>
            {/if}
        </div>
    {:else}
        <div class="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
            <Container>
                <Row>
                    <Col class="text-center">
                        <h1 class="text-xl font-bold text-red-800">No tienes acceso a esta página </h1>
                        <p class="text-lg text-black-600">Serás redirigido al login en 8 segundos... </p>
                    </Col>
                </Row>
            </Container>
        </div>
    {/if}
</main>

<style>
    @import "/styles.css";
    @import url('https://fonts.googleapis.com/css2?family=Rubik:ital,wght@0,300..900;1,300..900&display=swap');


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