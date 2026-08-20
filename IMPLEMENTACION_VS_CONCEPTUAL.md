# Auditoría de cumplimiento del documento conceptual

Fecha: 2026-08-18

## Resultado ejecutivo

La versión original implementaba principalmente el flujo mínimo **donación → matching → chat → entrega → confirmación → calificación → historial**. El documento conceptual era considerablemente más amplio: usuarios y roles, catálogos, administración, búsqueda avanzada, fotografías, vencimientos, notificaciones, dashboard, asistente, reportes de impacto y capacidades de IA.

Esta entrega amplía la aplicación para cubrir esas áreas con una implementación local orientada al curso.

## Matriz

| Área conceptual | Versión original | Nueva implementación | Observación |
|---|---|---|---|
| Registro de usuario | Parcial | Completo | Wizard, datos personales, ubicación, rol y aceptación legal. |
| Roles | No | Completo | Particular, rescatista, hogar de tránsito, ONG, veterinaria, comercio y admin. |
| Verificación de correo | No | Parcial/Local | Estado y token preparados; la entrega no depende de SMTP y marca la cuenta activa en entorno académico. |
| Donaciones | Parcial | Completo | Tipo, categoría, descripción, cantidad, estado, ubicación, vencimiento, presentación, envase, entrega, urgencia y foto. |
| Reglas de medicamentos | No | Completo | Vencimiento, presentación, envase e invalidación de vencidos/abiertos/sin identificación/ilegibles. |
| Fotografías | No | Completo básico | JPG/PNG, almacenamiento local, análisis de reglas y soporte de fotografías adicionales. |
| IA sobre publicaciones | No | Parcial intencional | Servicio desacoplado `services/ai.py`, modo Fase 2 basado en reglas; no se requiere proveedor externo. |
| Solicitudes | Parcial | Completo | Recurso, categoría, cantidad, justificación, prioridad, ubicación y vigencia. |
| Búsqueda | No | Completo | Filtros, distancia, urgencia y ordenamiento. |
| Búsquedas favoritas | No | Completo básico | Persistencia y alertas internas. |
| Matching | Parcial | Completo | Tipo, categoría, distancia, ubicación, cantidad, vencimiento, prioridad y urgencia. |
| Notificaciones | No | Completo básico | Persistencia y eventos internos. Push/SMS/email quedan como futuras integraciones. |
| Alertas vencimiento | No | Completo básico | Escaneo al consultar donaciones/notificaciones y alerta hasta 14 días. |
| Chat | Sí | Completo | Persistencia y autorización por coincidencia. Polling en frontend. |
| Entrega/confirmación | Sí | Completo | Reserva, entrega, confirmación bilateral y cierre. |
| Historial | Sí | Completo | No se expone eliminación. |
| Calificaciones/reputación | Sí | Completo | 1–5, comentario, promedio y conteo. |
| Dashboard personal | No | Completo básico | Actividad, reputación, estadísticas y vencimientos. |
| Perfil de publicación | No | Completo básico | Detalle, fotos, ubicación aproximada, donante, reputación y favorito. |
| Asistente virtual | No | Completo Fase 2 | Historial persistente, respuestas rápidas y escalamiento de soporte. |
| Soporte | No | Completo básico | Tickets internos. |
| Administración | No | Completo básico | Usuarios, categorías, campañas, comercios, membresías y cancelación administrativa. |
| Reportes impacto | No | Completo básico | Donaciones, entregas, usuarios, satisfacción, beneficiarios estimados y matching. |
| Catálogos | No | Completo básico | Categorías iniciales + alta/activación administrativa. |
| Email/Push/SMS | No | Futuro | El documento conceptual contempla algunos como futuros/opcionales; no se agregan proveedores externos. |
| OCR/visión/LLM real | No | Futuro | Se deja una interfaz local de IA para sustituir reglas por modelos reales. |

## Archivos principales agregados

- `backend/app/services/ai.py`
- `backend/app/services/notifications.py`
- `backend/app/routers/dashboard.py`
- `backend/app/routers/search.py`
- `backend/app/routers/notifications.py`
- `backend/app/routers/assistant.py`
- `backend/app/routers/admin.py`
- `backend/app/routers/catalogs.py`
- `backend/app/routers/support.py`
- `frontend/src/pages/Dashboard.jsx`
- `frontend/src/pages/Search.jsx`
- `frontend/src/pages/Assistant.jsx`
- `frontend/src/pages/Admin.jsx`
- `frontend/src/pages/DonationDetail.jsx`

## Validación técnica realizada

- Se ejecutó `python -m compileall` sobre todo el backend y no quedaron errores de sintaxis.
- El ZIP final excluye `__pycache__`, `.pyc`, `node_modules`, `dist` y bases SQLite generadas.
- No se pudo ejecutar una instalación/build completo dentro del entorno de generación porque este entorno no tiene acceso de red a PyPI/npm. El usuario ya comprobó que las dependencias Python originales se instalan correctamente en su equipo.

## Próximo nivel recomendado

Para una versión final de producción, sustituir los adaptadores locales por:

1. PostgreSQL + migraciones Alembic.
2. Almacenamiento de imágenes S3/MinIO.
3. Servicio de correo y verificación real.
4. OCR/visión por computadora para medicamentos/alimentos.
5. LLM/NLP para el asistente.
6. WebSockets para chat y push notifications.
7. Servicio de mapas/geocodificación.
8. Tests automatizados backend/frontend y CI/CD.

## Correcciones de la versión 2.1.0

- Corregido el correo técnico del administrador de `admin@donaciones.local` a `admin@redsolidaria.app`, porque Pydantic `EmailStr` considera `.local` un dominio reservado y rechazaba la respuesta de `/auth/me`.
- El arranque realiza una migración ligera del administrador existente si encuentra el correo anterior, por lo que no es obligatorio borrar la base únicamente para corregir este problema.
- Latitud y longitud del registro son realmente opcionales: cadenas vacías provenientes de formularios se convierten en `null` antes de la validación.
- Se agregaron validaciones de rango: latitud [-90, 90] y longitud [-180, 180]. Si se proporciona una coordenada se exige completar la otra.
- Se agregó un normalizador de errores de API para transformar errores de validación FastAPI/Pydantic (incluyendo listas de errores) en mensajes legibles para el usuario.
- Se agregó un `ErrorBoundary` de React para evitar pantallas completamente en blanco ante excepciones inesperadas de la interfaz.
- Se reforzó el manejo de errores en login, registro, dashboard, donaciones, solicitudes, coincidencias, chat, transacciones, búsqueda, asistente, administración y detalle de publicación.
