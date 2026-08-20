import axios from "axios";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "https://red-solidaria-rjb5.onrender.com";

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

/**
 * Convierte respuestas de FastAPI/Pydantic y errores de red en un mensaje
 * seguro y legible para mostrar en la interfaz.
 */
export function getApiErrorMessage(
  error,
  fallback = "Ocurrió un error. Intenta nuevamente.",
) {
  if (!error) return fallback;

  const detail = error.response?.data?.detail;

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        const location = Array.isArray(item?.loc)
          ? item.loc.filter((part) => part !== "body").join(" → ")
          : "";
        const message = item?.msg || "Dato inválido";
        return location ? `${location}: ${message}` : message;
      })
      .filter(Boolean);

    if (messages.length) return messages.join(" | ");
  }

  if (typeof detail === "string" && detail.trim()) return detail;
  if (typeof error.response?.data?.message === "string")
    return error.response.data.message;

  if (error.code === "ECONNABORTED" || error.message?.includes("timeout")) {
    return "El servidor tardó demasiado en responder. Verifica que el backend esté funcionando.";
  }

  if (!error.response && error.request) {
    return "No se pudo conectar con el servidor. Verifica que FastAPI esté ejecutándose en http://localhost:8000.";
  }

  if (error.response?.status === 401)
    return "Tu sesión no es válida o ha expirado. Inicia sesión nuevamente.";
  if (error.response?.status === 403)
    return "No tienes permisos para realizar esta operación.";
  if (error.response?.status === 404)
    return "No se encontró el recurso solicitado.";
  if (error.response?.status >= 500)
    return "El servidor encontró un problema. Revisa la consola del backend para más detalles.";

  return error.message || fallback;
}

export default client;
