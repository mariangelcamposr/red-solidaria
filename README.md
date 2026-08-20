# Red Solidaria de Donaciones para Mascotas

Implementación alineada con el documento conceptual **“Orquestación Agéntica Cíclica y Memoria Persistente”**. Es una aplicación académica full-stack para conectar donantes, solicitantes, rescatistas, ONG, veterinarias y comercios alrededor de medicamentos, alimentos, accesorios e insumos para mascotas.

## Arquitectura

- **Frontend:** React 18 + Vite + React Router + Axios.
- **Backend:** Python 3.12 + FastAPI + SQLAlchemy.
- **Persistencia:** SQLite (`backend/donaciones.db`).
- **Seguridad:** JWT + bcrypt.
- **IA Fase 2:** reglas locales para análisis de publicaciones y asistente virtual; la integración con un modelo real queda desacoplada en `backend/app/services/ai.py`.
- **Archivos:** fotografías JPG/PNG almacenadas en `backend/uploads/`.
- **Manejo de errores UI:** validaciones de FastAPI se traducen a mensajes legibles y existe una pantalla de recuperación para errores inesperados de React.

## Funcionalidades implementadas

1. Registro tipo wizard: datos personales, ubicación, perfil, aceptación de términos/privacidad.
2. Roles: particular, rescatista, hogar de tránsito, ONG, veterinaria, comercio y administrador.
3. Donaciones: tipo, categoría, descripción, cantidad, estado, ubicación, coordenadas, vencimiento, presentación, envase, condiciones de entrega, urgencia y fotografía.
4. Validaciones: categorías/tipos, fotografía JPG/PNG, cantidad positiva, vencimientos, requisitos especiales para medicamentos y contenido prohibido.
5. Solicitudes: recurso, categoría, cantidad, justificación, prioridad, ubicación y vigencia.
6. Búsqueda: categoría, tipo, ubicación, distancia, urgencia y ordenamiento por relevancia, cercanía, fecha, vencimiento o cantidad.
7. Búsquedas favoritas con alertas internas.
8. Matching automático: tipo, categoría, distancia, ubicación textual, cantidad, vencimiento, prioridad y urgencia; conserva criterios y puntaje.
9. Notificaciones internas: coincidencias, contacto, mensajes, vencimientos, entregas y reputación.
10. Chat privado por coincidencia con historial persistente.
11. Coordinación y confirmación mutua de entrega.
12. Historial inmutable a nivel funcional y reputación de 1 a 5.
13. Alertas de productos próximos a vencer.
14. Dashboard personal: donaciones, solicitudes, coincidencias, transacciones, reputación, estadísticas y próximos vencimientos.
15. Asistente virtual persistente con respuestas predefinidas (Fase 2) y botón de soporte mediante tickets.
16. Administración: usuarios, categorías, campañas, comercios asociados, membresías, cancelación administrativa de publicaciones y reportes de impacto.
17. Reporte de impacto: donaciones, entregas, mascotas beneficiadas estimadas, categorías, usuarios, satisfacción y tasa de matching exitoso.
18. Catálogos iniciales precargados.

## Qué no se implementa como servicio externo real

El documento conceptual contempla correo electrónico, push/SMS, OCR/visión por computadora, NLP/LLM, mapas y notificaciones externas como capacidades futuras o dependientes de proveedores. Para que el trabajo sea ejecutable sin cuentas externas, la entrega implementa una versión académica local:

- verificación de correo simulada/local;
- IA Fase 2 basada en reglas, con resultado persistido;
- asistente conversacional basado en reglas;
- notificaciones dentro de la aplicación;
- coordenadas + distancia Haversine, sin proveedor de mapas;
- soporte mediante tickets internos.

Las piezas están separadas para poder sustituirse posteriormente por un proveedor de correo, OCR/visión, LLM, mapas o push.

## Levantar en Windows

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Swagger: `http://localhost:8000/docs`

### Frontend

En otra terminal:

```powershell
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173`

## Manejo de errores y coordenadas opcionales

- Latitud y longitud en el registro son realmente opcionales: si se dejan vacías, el frontend envía `null` y el backend las almacena como `NULL`.
- Si se proporciona una coordenada, se valida su rango y se exige completar la pareja latitud/longitud.
- Los errores de validación de FastAPI/Pydantic se muestran en la interfaz en lugar de intentar renderizar directamente el arreglo de errores.
- Un error inesperado de React ya no deja la pantalla completamente en blanco: se muestra una pantalla de recuperación con opción de recargar.

## Importante al actualizar desde la versión anterior

La versión anterior tenía un esquema SQLite diferente. Si ya ejecutaste aquella versión y existe `backend/donaciones.db`, para una instalación limpia de esta entrega elimina ese archivo antes del primer arranque; `create_all()` creará el nuevo esquema.

Si conservas la base de la versión anterior, esta versión corrige automáticamente el correo del administrador creado como `admin@donaciones.local` a `admin@redsolidaria.app`.

No borres el historial desde la aplicación: el modelo no expone eliminación de transacciones.

## Administrador local

Al iniciar, se crea automáticamente un administrador de desarrollo si no existe:

- usuario: `admin`
- correo técnico: `admin@redsolidaria.app`
- contraseña: `admin123`

Podés cambiar estos valores mediante `ADMIN_USERNAME`, `ADMIN_EMAIL` y `ADMIN_PASSWORD`. **No uses estas credenciales en producción.**

## Flujo de prueba recomendado

1. Levantar backend y frontend.
2. Registrar un solicitante y crear una solicitud de alimentos con prioridad alta.
3. Registrar un donante y publicar una donación con fotografía, cantidad y misma categoría/ubicación.
4. Revisar Dashboard/Notificaciones/Coincidencias.
5. Contactar y utilizar el chat.
6. Coordinar fecha/hora/lugar y marcar entrega.
7. Confirmar desde ambos usuarios.
8. Calificar mutuamente.
9. Revisar reputación e historial.
10. Probar Búsqueda y guardar una búsqueda favorita.
11. Entrar con `admin/admin123` y revisar reportes, usuarios y catálogos.
12. Probar el asistente virtual.


## Corrección 2.1.1

Se corrigió la definición del schema `TransactionCoordinate` utilizado por el endpoint `POST /transactions/{match_id}/coordinate`. La versión 2.1.0 referenciaba el schema desde el router pero no lo había declarado en `schemas.py`, lo que impedía que Uvicorn cargara la aplicación. También se agregó una validación de compilación de los módulos Python antes de la entrega.
