<style>
    @import "/styles.css";
    @import url('https://fonts.googleapis.com/css2?family=Rubik:ital,wght@0,300..900;1,300..900&display=swap');
</style>

<svelte:head>
    <script src="https://cdn.tailwindcss.com"></script>
</svelte:head>

<script>
    import { Container, Row, Col, Card, CardHeader, CardBody, CardTitle, CardSubtitle, CardText, Button} from '@sveltestrap/sveltestrap';
    import Fa from 'svelte-fa';
    import {faGithub} from '@fortawesome/free-brands-svg-icons';

</script>

<main class="bg-gradient-to-b from-blue-100 via-white to-blue-50 min-h-screen py-10 px-6">
    <div class="max-w-5xl mx-auto p-6 bg-white rounded-xl shadow-xl border border-gray-200">
        
        <header class="text-center mb-10">
            <h1 class="text-4xl font-bold text-blue-900">🏀 BasketVision</h1>
            <p class="text-lg mt-2 text-gray-600">
                Análisis inteligente de partidos de baloncesto en video.
            </p>
        </header>

        <section class="intro text-center mb-12">
            <h2 class="text-2xl font-semibold text-gray-800">¿Qué es BasketVision?</h2>
            <p class="mt-4 text-gray-600 max-w-3xl mx-auto">
                BasketVision es una plataforma web que permite analizar partidos de baloncesto de forma automática a partir de un vídeo. Detecta jugadores, árbitros, balón, canastas, asigna equipos, calcula estadísticas de posesión, convierte coordenadas reales a una vista táctica, y genera un video final con todas las anotaciones visuales.
            </p>
        </section>

        <section class="features mb-12">
            <h2 class="text-2xl font-semibold text-gray-800 mb-4 text-center">🔍 Funcionalidades</h2>
            <ul class="list-disc list-inside text-gray-700 space-y-3 px-6">
                <li><strong>📹 Subida de vídeo:</strong> analiza un partido directamente desde tu navegador.</li>
                <li><strong>🧠 Detección de objetos:</strong> jugadores, árbitros, balón y canasta usando modelos YOLO.</li>
                <li><strong>👕 Asignación de equipos:</strong> mediante clustering automático por colores.</li>
                <li><strong>⏱️ Estadísticas de posesión:</strong> seguimiento por frame de quién controla el balón.</li>
                <li><strong>🏀 Detección de canastas:</strong> muestra un cartel cada vez que se detecta un tiro convertido.</li>
                <li><strong>📐 Homografía:</strong> transforma coordenadas a una vista cenital (2D del campo).</li>
                <li><strong>🎨 Renderizado visual:</strong> el video final incluye anotaciones superpuestas en tiempo real.</li>
            </ul>
        </section>

         <section class="video-demo mb-12 text-center">
            <h2 class="text-2xl font-semibold text-gray-800 mb-4">🎥 Vídeo Demo</h2>
            <!--
            <video class="rounded-lg shadow-lg mx-auto" width="720" height="420" controls>
                <source src="/demo.mp4" type="video/mp4" />
                Tu navegador no soporta la reproducción de video.
            </video>
            -->
        </section>

        <section class="resources text-center mb-12">
            <h2 class="text-2xl font-semibold text-gray-800 mb-4">📚 Recursos del Proyecto</h2>
            <div class="flex flex-col md:flex-row justify-center items-center gap-6">
                <a href="https://github.com/josmarsua/TFG" target="_blank" class="flex items-center space-x-2 bg-gray-900 text-white px-6 py-2 rounded-full shadow hover:bg-gray-700 transition">
                    <Fa icon={faGithub} />
                    <span>Repositorio en GitHub</span>
                </a>

                <a href="/" target="_blank" class="bg-blue-600 text-white px-6 py-2 rounded-full shadow hover:bg-blue-700 transition">
                    Ver Memoria del Proyecto 📄
                </a>
            </div>
        </section>

        <section class="cta text-center mt-12">
            <h3 class="text-xl font-semibold text-gray-800 mb-2">¿Listo para comenzar?</h3>
            <p class="text-gray-600 mb-4">Regístrate o inicia sesión para subir un vídeo.</p>
            <div class="space-x-4">
                <a href="/register" class="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-full shadow-md transition">Registrarse</a>
                <a href="/login" class="bg-gray-100 hover:bg-gray-200 text-gray-800 py-2 px-4 rounded-full border transition">Iniciar sesión</a>
            </div>
        </section>
    </div>
</main>
