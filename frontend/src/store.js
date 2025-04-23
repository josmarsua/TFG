import { writable } from "svelte/store";
import { browser } from "$app/environment"; 

const initialToken = browser ? localStorage.getItem("token") || "" : "";

export const authToken = writable(initialToken);

// Función global para cerrar sesión correctamente:
export function forceLogout() {
    authToken.set("");  // Esto ya limpia el localStorage
    if (browser) {
        window.location.href = "/login";  // Redirigir al login
    }
}

// Suscripción para mantener localStorage actualizado:
if (browser) {
    authToken.subscribe(value => {
        if (value) {
            localStorage.setItem("token", value);
        } else {
            localStorage.removeItem("token");
        }
    });
}
