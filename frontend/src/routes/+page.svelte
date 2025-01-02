<script>
    let file = null;
    let processedFile = null;
    let trajectoryFile = null;

    async function uploadFile() {
        if (!file) {
            alert("Por favor, selecciona un archivo");
            return;
        }

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
        } catch (error) {
            alert(error.message);
        }
    }
</script>

<main>
    <h1>Sube tu video de baloncesto</h1>
    <input type="file" accept="video/*" on:change="{e => file = e.target.files[0]}" />
    <button on:click="{uploadFile}">Subir</button>

    {#if processedFile && trajectoryFile}
        <h2>Resultados</h2>
        <p><a href="{processedFile}" download>Descargar Video Procesado</a></p>
        <p><a href="{trajectoryFile}" download>Descargar Video de Trayectorias</a></p>
    {/if}
</main>
