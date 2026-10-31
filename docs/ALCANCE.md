# Ruta mínima para cumplir el enunciado

Fuente: Proyecto1-ii2026 (1).pdf proporcionado por el usuario.
La prioridad actual es probar los dos circuitos; esta lista evita confundir esa
primera prueba con la entrega completa. No se implementa el extra de velocidad.

| Obligatorio | Estado de esta primera entrega |
|---|---|
| Dos Faros soldados, emisor/receptor, indicadores, botón, headers | Diseño preliminar; montaje y validación pendientes |
| Esquemático, BOM CRC, fotos y bitácora de multímetro | Guía preliminar; documentos finales pendientes |
| Tramas <=128 bytes, versión, CRC, biblioteca DispositivoLuzAdaptador | Implementado y probado en software |
| Acceso al medio | Sondeo A/B mínimo; no multiiniciador |
| Dirección persistente y rotable | Implementado en archivo de SD |
| Goodput y BER a tres distancias | Resumen de goodput implementado; mediciones físicas y BER pendientes |
| Mesh dinámica sobre Ethernet, WiFi y Faro; dos comunidades | Pendiente |
| Directorio con entradas firmadas | Pendiente |
| Modelo de amenazas; intermediarios sin origen y destino simultáneos | Pendiente; planificar rutas por capas, no reenviar identidad de origen |
| Cifrado E2E con biblioteca reconocida, padding | Padding de enlace implementado; criptografía pendiente |
| Pánico con borrado de llaves, sin registros sensibles, TTL | Detención local preliminar; zeroize y política integral pendientes |
| Chat o microblogging privado interno | Pendiente |
| Gateway autenticado con protección anti-replay | Pendiente |
| Workers gratuito: salas DO/WebSocket, RSS/Atom, dead drop | Pendiente |
| Directorio público verificable y rate limit | Pendiente |
| Wrangler reproducible y secretos fuera de Git | Pendiente |
| RFC ASCII, privacidad y seguridad | Descripción inicial de trama; RFC pendiente |
| Documentación, kick-off, evidencias, autoevaluación | Pendiente; no inventar resultados ni actividades |

Arquitectura final mínima prevista:

```text
nodo + controlador A <--- luz ---> controlador B + gateway Raspberry Pi
       |                                   |
       +------ nodos mesh por TCP/IP ------+
                                           |
                                         HTTPS
                                           |
                                   Cloudflare Worker
                                 / salas / feed / blobs
```

Se confirmaron dos Raspberry Pi 2 B: una por extremo óptico. Para demostrar
enrutamiento y anonimato se necesitarán procesos/nodos adicionales en la mesh.
Usar Python para nodos/gateway y JavaScript para Worker
mantiene el conjunto pequeño y dentro de los lenguajes permitidos.
