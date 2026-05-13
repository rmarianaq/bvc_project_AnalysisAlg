/**
 * Configuración de la aplicación
 * 
 * La URL del API se determina automáticamente:
 * - Desarrollo local: http://localhost:8000
 * - Producción (Nginx): /api (proxy configurado en Nginx)
 */

// Detectar si estamos en desarrollo o producción
const isDevelopment = window.location.hostname === 'localhost' || 
                      window.location.hostname === '127.0.0.1';

// Configurar URL del API
export const API_BASE_URL = isDevelopment 
  ? 'http://localhost:8000'  // Desarrollo local
  : '/api';                   // Producción (Nginx hace proxy a :8000)

// Exportar configuración
export default {
  API_BASE_URL
};
