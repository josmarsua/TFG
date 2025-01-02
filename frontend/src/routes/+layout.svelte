<script>
    import Footer from './Footer.svelte';
    import Header from './Header.svelte';
</script>

<svelte:head>
    <title>TFG josmarsua</title>
    <script src="https://cdn.tailwindcss.com"></script>
</svelte:head>

<div class="bg-teal-100 min-h-screen flex flex-col">
    <Header />
    <main class="flex-1 py-6">
        <slot></slot>
    </main>
    <Footer />
</div>
