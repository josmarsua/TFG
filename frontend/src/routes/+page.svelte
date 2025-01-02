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
</script>

<main>
    <div class="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
        <header class="text-center mb-8">
            <h1 class="text-3xl font-bold text-gray-800">Bienvenido/a a [nombre APP]</h1>
            <p class="text-lg text-gray-600">
                [descripción APP]
            </p>
        </header>
    
        <section class="intro text-center mb-8">
            <h2 class="text-2xl font-semibold text-gray-800">Sobre mi proyecto</h2>
            <p class="mt-4 text-gray-600">
                [descripción proyecto]
            </p>
        </section>
    
        <section class="features mb-8">
            <h2 class="text-2xl font-semibold text-gray-800">Funcionalidades</h2>
            <ul class="list-disc list-inside mt-4 text-gray-600">
                <li><strong>Funcionalidad 1:</strong> descripción</li>
                <li><strong>Funcionalidad 2:</strong> descripción</li>
            </ul>
        </section>
    </div>
</main>

