    <svelte:head>
        <script src="https://cdn.tailwindcss.com"></script>
    </svelte:head>

    <header class="bg-blue-900 p-4 text-white">
        <div class="max-w-4xl mx-auto flex justify-between items-center">
            <div class="text-xl font-bold">
                <a href="/">TFG josmarsua</a> <!-- Link to the home page -->
            </div>
            <div class="space-x-4">
                <a href="/process" class="bg-blue-500 hover:bg-blue-700 font-semibold py-2 px-4 rounded">Analizar</a>
                <a href="/" class="bg-green-500 hover:bg-green-700 font-semibold py-2 px-4 rounded">Demo</a>
                <!--
                {% if user.is_authenticated %}
                <form action="{% url 'logout' %}" method="post" class="inline">
                    {% csrf_token %}
                    <button type="submit" class="bg-red-500 hover:bg-red-700 font-semibold py-2 px-4 rounded">Log Out</button>
                </form>
                {% endif %}
                -->
            </div>
        </div>
    </header>
