# TaskFlow AI — Project Specs

## Descripción

TaskFlow AI es un gestor personal de tareas con dos capacidades de IA:

1. **Procesamiento al crear** — cuando el usuario crea una tarea en lenguaje natural, una IA la clasifica, le asigna prioridad sugerida y extrae fecha objetivo si la hay.
2. **RAG sobre el histórico** — el usuario puede preguntar en lenguaje natural sobre sus tareas pasadas y obtener respuestas con contexto recuperado del propio histórico.

Todo se persiste en PostgreSQL. Los embeddings se guardan en pgvector. No hay autenticación compleja: usuario único o auth básica.

## Objetivo del proyecto en el curso

No es un producto. Es un **codebase realista pero acotado** sobre el que practicar:

- describir la arquitectura a la IA con `CLAUDE.md` / `AGENTS.md`
- crear skills custom que generen código siguiendo las convenciones del proyecto
- usar modo plan, subagentes y tool use con un caso real
- aplicar guardrails de equipo

## User Stories

### Epic 1 — Gestión básica de tareas

#### US-001 — Ver lista de tareas

Como usuario, quiero ver una lista de mis tareas para conocer mi trabajo pendiente.

**Criterios de aceptación**

- Lista vacía con mensaje "No hay tareas" inicialmente
- Cada tarea muestra: título, prioridad (badge de color), estado, fecha objetivo si la hay
- Orden por fecha de creación, más recientes primero
- Paginación de 20 en 20

#### US-002 — Crear tarea en lenguaje natural

Como usuario, quiero escribir una tarea en lenguaje natural y que la IA extraiga campos estructurados.

**Criterios de aceptación**

- Input único de texto libre, ej: `"Llamar al cliente Pérez mañana por la mañana, urgente"`
- Al enviar, una llamada al backend invoca a la IA y devuelve:
  - `title`: resumen corto
  - `description`: el texto original
  - `priority`: `low | medium | high` (sugerida por IA, editable)
  - `due_date`: fecha extraída si la hay, null si no
  - `tags`: lista de etiquetas sugeridas
- El usuario revisa los campos extraídos en un formulario y confirma o edita
- La tarea aparece en la lista al confirmar

**Notas técnicas**

- el backend expone `POST /api/tasks/parse/` que devuelve los campos sin guardar
- el guardado real es `POST /api/tasks/` con los campos ya validados

#### US-003 — Editar tarea

Como usuario, quiero editar una tarea existente para corregir información.

**Criterios de aceptación**

- Botón "Editar" abre formulario con datos actuales
- Mismos campos que crear, sin pasar por la IA
- "Guardar" actualiza, "Cancelar" descarta

#### US-004 — Eliminar tarea

Como usuario, quiero eliminar una tarea.

**Criterios de aceptación**

- Botón "Eliminar" con confirmación
- Soft delete: la tarea se marca como `deleted_at` para que el RAG histórico siga teniendo contexto

### Epic 2 — Estados y filtros

#### US-005 — Cambiar estado de una tarea

**Criterios**

- Estados: `TODO → IN_PROGRESS → DONE`
- Botón visible para avanzar/retroceder
- Contador por estado en la cabecera

#### US-006 — Filtrar por estado y prioridad

**Criterios**

- Tabs por estado: Todas, Pendientes, En curso, Completadas
- Filtro por prioridad combinable
- Mantener filtro al crear o editar

### Epic 3 — RAG sobre histórico

#### US-007 — Indexar tarea para búsqueda semántica

Cada vez que se crea, edita o completa una tarea, el sistema genera un embedding y lo guarda en pgvector.

**Criterios técnicos**

- tabla `task_embeddings` con FK a `tasks`, columna `embedding vector(1536)`
- al crear/editar tarea → reindexar
- al borrar (soft delete) → marcar como inactivo, no borrar embedding
- el job de indexado puede ser síncrono al inicio (simple); refactor a async como ejercicio

#### US-008 — Preguntar al histórico en lenguaje natural

Como usuario, quiero hacer preguntas sobre mis tareas pasadas en lenguaje natural.

**Criterios de aceptación**

- Input de pregunta tipo: `"¿Qué tareas hice la semana pasada relacionadas con el cliente Pérez?"`
- El backend:
  1. genera embedding de la pregunta
  2. recupera top-K tareas más relevantes (k=5)
  3. pasa pregunta + tareas como contexto a la IA
  4. devuelve respuesta + lista de tareas referenciadas
- La UI muestra la respuesta y permite hacer click en cada tarea referenciada para verla
- Si no hay contexto suficiente, la IA debe responder explícitamente "no encuentro tareas relacionadas con eso"

**Reglas anti-alucinación**

- la IA no puede inventar tareas que no estén en el contexto recuperado
- la respuesta debe citar IDs de tarea concretos
- si la pregunta no tiene relación con tareas, la IA debe rechazarla cortésmente

### Epic 4 — Persistencia y export

#### US-009 — Exportar tareas a JSON

**Criterios**

- Botón "Exportar" descarga `taskflow_export_YYYY-MM-DD.json`
- Incluye todas las tareas no borradas con todos sus campos
- Formato JSON indentado

## Modelo de datos

```python
class Task(models.Model):
    id: UUID  # PK
    title: str  # 3-200 chars
    description: str  # texto libre, puede ser largo
    priority: Literal["low", "medium", "high"]
    status: Literal["TODO", "IN_PROGRESS", "DONE"]
    due_date: date | None
    tags: list[str]  # ArrayField
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None  # soft delete

class TaskEmbedding(models.Model):
    id: UUID
    task: ForeignKey[Task]
    embedding: VectorField(dimensions=1536)
    model_name: str  # qué modelo generó el embedding
    created_at: datetime
```

## Reglas de negocio

- los estados solo avanzan o retroceden 1 paso a la vez
- la prioridad por defecto si la IA no la determina es `medium`
- las tareas borradas (soft) no aparecen en la lista pero sí en el RAG histórico
- el reindexado es obligatorio tras cualquier edición que toque `title`, `description` o `tags`
- los embeddings se versionan por `model_name` para permitir reindexado masivo si se cambia de modelo

## API objetivo (resumen)

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/tasks/` | listar con filtros |
| `POST` | `/api/tasks/` | crear tarea (campos ya estructurados) |
| `POST` | `/api/tasks/parse/` | parsear lenguaje natural → campos sugeridos |
| `GET` | `/api/tasks/{id}/` | detalle |
| `PATCH` | `/api/tasks/{id}/` | editar |
| `DELETE` | `/api/tasks/{id}/` | soft delete |
| `POST` | `/api/tasks/{id}/transition/` | cambiar estado |
| `POST` | `/api/tasks/ask/` | RAG sobre histórico |
| `GET` | `/api/tasks/export/` | export JSON |

## Lo que NO entra en el alcance del demo

- multiusuario complejo / permisos
- notificaciones
- recordatorios automáticos
- integraciones con calendarios externos
- móvil (Flutter está fuera del piloto)
- evaluación automática del RAG (queda como ejercicio)

## Decisiones técnicas pendientes (a tomar en el curso)

- proveedor LLM por defecto (Anthropic, OpenAI o local)
- modelo de embeddings concreto
- estrategia de chunking si las descripciones se vuelven largas
- estrategia de invalidación de cache de embeddings
