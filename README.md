# AITasks — Gestor de tareas con IA

> Repositorio de demostración para el curso **AI Engineering — Piloto Barcelona**.
> Sirve como base sobre la que practicar el framework de trabajo con IA
> (Claude Code, OpenCode y similares) aplicado a un stack real Django + React.

## Qué es esto

Un mini-proyecto **AITasks** — gestor de tareas personales con dos giros planificados:

1. **IA procesa las tareas** al crearlas (clasificación, prioridad sugerida, extracción de fechas).
2. **RAG sobre el histórico de tareas** — el usuario puede preguntar en lenguaje natural sobre sus tareas pasadas.

Es **deliberadamente sencillo**. No es un producto, es un campo de pruebas para enseñar el método de trabajo con IA sobre un stack realista.

## Estado actual — Sprint 1 (MVP sin IA)

Backend Django + DRF completamente funcional:

- CRUD completo de tareas (crear, listar, detalle, editar, borrado lógico)
- Transiciones de estado controladas (TODO <-> IN_PROGRESS <-> DONE)
- Filtros por estado y prioridad combinables
- Paginación (20 por defecto, configurable)
- Formato de errores consistente (`{"error": {"code", "message", "details"}}`)
- 104 tests pasando

**Fuera del Sprint 1**: frontend React, parsing con IA, embeddings, RAG, export JSON.

## Stack

| Capa | Tecnologia | Notas |
|------|-----------|-------|
| Backend | Django 5.1 + DRF 3.15 | API REST |
| Base de datos | SQLite | desarrollo local, migrable a PostgreSQL |
| Filtros | django-filter 24.x | por status y priority |
| Frontend | pendiente (Sprint 2+) | React planificado |
| IA | pendiente (Sprint 3+) | proveedor agnostico via adapter |

## Requisitos previos

- Python 3.11 o superior
- `uv` (recomendado) o `pip`

## Instalacion y arranque

### 1. Clonar el repositorio

```bash
git clone <url-del-repo>
cd repo-demo
```

### 2. Crear entorno virtual e instalar dependencias

Con `uv` (recomendado):

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Con `pip`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Aplicar migraciones

```bash
python manage.py migrate
```

Esto crea el archivo `db.sqlite3` con la tabla de tareas.

### 4. Arrancar el servidor de desarrollo

```bash
python manage.py runserver
```

El servidor arranca en `http://localhost:8000`.

## Endpoints de la API

Base path: `/api/tasks/`

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| `GET` | `/api/tasks/` | Listar tareas (paginado, con filtros) |
| `POST` | `/api/tasks/` | Crear tarea |
| `GET` | `/api/tasks/{id}/` | Detalle de tarea |
| `PATCH` | `/api/tasks/{id}/` | Editar tarea (parcial) |
| `DELETE` | `/api/tasks/{id}/` | Borrado logico (soft delete) |
| `POST` | `/api/tasks/{id}/transition/` | Cambiar estado (forward/backward) |

### Filtros disponibles (query params)

- `?status=TODO` / `IN_PROGRESS` / `DONE`
- `?priority=low` / `medium` / `high`
- `?page=2&page_size=10`
- Filtros combinables: `?status=TODO&priority=high`

### Ejemplo: crear tarea

```bash
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Preparar presentacion del curso", "priority": "high", "due_date": "2026-04-15", "tags": ["curso", "barcelona"]}'
```

### Ejemplo: transicion de estado

```bash
# Mover de TODO a IN_PROGRESS
curl -X POST http://localhost:8000/api/tasks/{id}/transition/ \
  -H "Content-Type: application/json" \
  -d '{"direction": "forward"}'
```

### DRF Browsable API

Navega a `http://localhost:8000/api/tasks/` en el navegador para usar la interfaz web interactiva de DRF.

## Tests

```bash
# Suite completa (104 tests)
python manage.py test tasks

# Con detalle
python manage.py test tasks -v2

# Modulo especifico
python manage.py test tasks.tests.test_views
python manage.py test tasks.tests.test_models
python manage.py test tasks.tests.test_serializers
python manage.py test tasks.tests.test_services
```

## Estructura del proyecto

```
repo-demo/
├── manage.py                 # Entry point de Django
├── requirements.txt          # Dependencias Python
├── aitasks/                  # Paquete del proyecto Django
│   ├── settings.py           # Configuracion (apps, REST_FRAMEWORK, SQLite)
│   ├── urls.py               # URLs raiz (/admin/, /api/)
│   ├── exceptions.py         # Handler de errores personalizado
│   └── wsgi.py
├── tasks/                    # App de tareas
│   ├── models.py             # Modelo Task (UUID, soft delete, indices)
│   ├── managers.py           # AliveManager (excluye borradas por defecto)
│   ├── serializers.py        # TaskSerializer + TransitionSerializer
│   ├── services.py           # Maquina de estados (funcion pura)
│   ├── views.py              # TaskViewSet (CRUD + transition)
│   ├── filters.py            # Filtros por status y priority
│   ├── urls.py               # Router DRF
│   ├── admin.py              # Admin con acceso a tareas borradas
│   └── tests/                # 104 tests
│       ├── test_models.py
│       ├── test_serializers.py
│       ├── test_services.py
│       └── test_views.py
├── docs/                     # Documentacion de diseno
│   ├── diseno-base-de-datos.md
│   ├── diseno-endpoints.md
│   └── logica-negocio.md
├── openspec/                 # Artefactos SDD (planificacion)
└── PRD.md                    # Product Requirements Document
```

## Modelo de datos

```
Task
 ├── id: UUID (PK, auto)
 ├── title: string (3-200 chars)
 ├── description: text (opcional)
 ├── priority: low | medium | high (default: medium)
 ├── status: TODO | IN_PROGRESS | DONE (default: TODO)
 ├── due_date: date (opcional)
 ├── tags: string[] (JSON, deduplicados)
 ├── created_at: datetime (auto)
 ├── updated_at: datetime (auto)
 └── deleted_at: datetime (soft delete)
```

### Maquina de estados

```
TODO ──forward──> IN_PROGRESS ──forward──> DONE
TODO <──backward── IN_PROGRESS <──backward── DONE
```

Solo se puede avanzar o retroceder un paso por vez. No se permiten saltos.

## Documentacion del proyecto

- [`PRD.md`](./PRD.md) — Requisitos funcionales completos (incluye sprints futuros con IA)
- [`docs/`](./docs/) — Diseno tecnico del Sprint 1 (base de datos, endpoints, logica de negocio)
- [`openspec/`](./openspec/) — Artefactos de planificacion SDD

## Licencia

MIT
