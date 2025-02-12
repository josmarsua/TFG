import { writable } from "svelte/store";
import { browser } from "$app/environment"; // Verifica si estamos en el navegador

// Inicializar el store con un valor vacío si estamos en el servidor
const initialToken = browser ? localStorage.getItem("token") || "" : "";

export const authToken = writable(initialToken);

// Solo actualizar localStorage si estamos en el navegador
if (browser) {
    authToken.subscribe(value => {
        if (value) {
            localStorage.setItem("token", value);
        } else {
            localStorage.removeItem("token");
        }
    });
}
