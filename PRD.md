# PRD — AITasks

> Gestor personal de tareas con capacidades de IA para clasificación automática y consulta semántica del histórico.

**Versión**: 1.0  
**Fecha**: 2026-04-09  
**Estado**: Draft  
**Autor**: Fran BlakIA

---

## 1. Problema y oportunidad

Los gestores de tareas tradicionales requieren que el usuario estructure manualmente cada tarea (título, prioridad, fecha, etiquetas). Esto genera fricción y hace que muchas tareas se registren incompletas o directamente no se registren.

Además, el histórico de tareas completadas queda enterrado en listas que nadie consulta, perdiendo contexto valioso sobre qué se hizo, cuándo y por qué.

**AITasks** resuelve ambos problemas:

1. **Procesamiento al crear** — el usuario escribe en lenguaje natural y una IA extrae campos estructurados (título, prioridad, fecha, etiquetas).
2. **RAG sobre el histórico** — el usuario pregunta en lenguaje natural sobre sus tareas pasadas y obtiene respuestas con contexto recuperado.

## 2. Objetivo del proyecto

Este NO es un producto. Es un **codebase realista pero acotado** diseñado como material de un curso para practicar:

- Describir la arquitectura a la IA con `CLAUDE.md` / `AGENTS.md`
- Crear skills custom que generen código siguiendo convenciones del proyecto
- Usar modo plan, subagentes y tool use con un caso real
- Aplicar guardrails de equipo

### 2.1 Métricas de éxito

| Métrica | Target |
|---------|--------|
| Cobertura funcional | Todas las US de Epic 1 y Epic 2 implementadas |
| IA — parsing | La IA extrae correctamente título, prioridad y fecha en >80% de inputs naturales |
| IA — RAG | Las respuestas citan tareas reales (0 alucinaciones en el contexto recuperado) |
| Experiencia curso | Los participantes pueden ejecutar el flujo completo en <2h de workshop |

## 3. Alcance

### 3.1 Dentro del alcance

- CRUD completo de tareas (crear, leer, editar, soft delete)
- Parsing de lenguaje natural → campos estructurados via IA
- Estados con transiciones controladas (TODO → IN_PROGRESS → DONE)
- Filtros por estado y prioridad
- Indexado semántico de tareas (embeddings)
- RAG: preguntas en lenguaje natural sobre el histórico
- Export a JSON
- Usuario único o auth básica

### 3.2 Fuera del alcance

- Multiusuario complejo / permisos
- Notificaciones
- Recordatorios automáticos
- Integraciones con calendarios externos
- Móvil (Flutter está fuera del piloto)
- Evaluación automática del RAG (queda como ejercicio)

## 4. Supuestos y restricciones

### Supuestos

- La persistencia concreta se adaptará al stack final del demo
- No hay autenticación compleja: usuario único o auth básica
- El volumen de tareas será bajo (<1000), no se requiere optimización de escala
- Los participantes del curso tienen conocimientos básicos de Python y APIs REST

### Restricciones

- El proyecto debe ser ejecutable en un entorno local sin infraestructura cloud obligatoria
- Las llamadas a IA deben poder funcionar con al menos un proveedor LLM (ver decisiones pendientes)

## 5. User Stories

### Epic 1 — Gestión básica de tareas (Must Have)

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

- El backend expone `POST /api/tasks/parse/` que devuelve los campos sin guardar
- El guardado real es `POST /api/tasks/` con los campos ya validados

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

### Epic 2 — Estados y filtros (Must Have)

#### US-005 — Cambiar estado de una tarea

**Criterios de aceptación**

- Estados: `TODO → IN_PROGRESS → DONE`
- Botón visible para avanzar/retroceder
- Contador por estado en la cabecera

#### US-006 — Filtrar por estado y prioridad

**Criterios de aceptación**

- Tabs por estado: Todas, Pendientes, En curso, Completadas
- Filtro por prioridad combinable
- Mantener filtro al crear o editar

### Epic 3 — RAG sobre histórico (Should Have)

#### US-007 — Indexar tarea para búsqueda semántica

Cada vez que se crea, edita o completa una tarea, el sistema genera un embedding y lo guarda en una capa de persistencia preparada para búsqueda semántica.

**Criterios técnicos**

- Tabla o estructura equivalente para relacionar tareas y embeddings
- Al crear/editar tarea → reindexar
- Al borrar (soft delete) → marcar como inactivo, no borrar embedding
- El job de indexado puede ser síncrono al inicio (simple); refactor a async como ejercicio

#### US-008 — Preguntar al histórico en lenguaje natural

Como usuario, quiero hacer preguntas sobre mis tareas pasadas en lenguaje natural.

**Criterios de aceptación**

- Input de pregunta tipo: `"¿Qué tareas hice la semana pasada relacionadas con el cliente Pérez?"`
- El backend:
  1. Genera embedding de la pregunta
  2. Recupera top-K tareas más relevantes (k=5)
  3. Pasa pregunta + tareas como contexto a la IA
  4. Devuelve respuesta + lista de tareas referenciadas
- La UI muestra la respuesta y permite hacer click en cada tarea referenciada para verla
- Si no hay contexto suficiente, la IA debe responder explícitamente "no encuentro tareas relacionadas con eso"

**Reglas anti-alucinación**

- La IA no puede inventar tareas que no estén en el contexto recuperado
- La respuesta debe citar IDs de tarea concretos
- Si la pregunta no tiene relación con tareas, la IA debe rechazarla cortésmente

### Epic 4 — Persistencia y export (Could Have)

#### US-009 — Exportar tareas a JSON

**Criterios de aceptación**

- Botón "Exportar" descarga `aitasks_export_YYYY-MM-DD.json`
- Incluye todas las tareas no borradas con todos sus campos
- Formato JSON indentado

## 6. Modelo de datos

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
    embedding: list[float] | persisted_embedding_reference
    model_name: str  # qué modelo generó el embedding
    created_at: datetime
```

## 7. Reglas de negocio

- Los estados solo avanzan o retroceden 1 paso a la vez
- La prioridad por defecto si la IA no la determina es `medium`
- Las tareas borradas (soft) no aparecen en la lista pero sí en el RAG histórico
- El reindexado es obligatorio tras cualquier edición que toque `title`, `description` o `tags`
- Los embeddings se versionan por `model_name` para permitir reindexado masivo si se cambia de modelo

## 8. API

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/tasks/` | Listar con filtros |
| `POST` | `/api/tasks/` | Crear tarea (campos ya estructurados) |
| `POST` | `/api/tasks/parse/` | Parsear lenguaje natural → campos sugeridos |
| `GET` | `/api/tasks/{id}/` | Detalle |
| `PATCH` | `/api/tasks/{id}/` | Editar |
| `DELETE` | `/api/tasks/{id}/` | Soft delete |
| `POST` | `/api/tasks/{id}/transition/` | Cambiar estado |
| `POST` | `/api/tasks/ask/` | RAG sobre histórico |
| `GET` | `/api/tasks/export/` | Export JSON |

## 9. Decisiones técnicas pendientes

| Decisión | Opciones | Estado |
|----------|----------|--------|
| Proveedor LLM por defecto | Anthropic, OpenAI o local | Pendiente |
| Modelo de embeddings | OpenAI, Cohere, local (sentence-transformers) | Pendiente |
| Estrategia de chunking | Si las descripciones se vuelven largas | Pendiente |
| Invalidación de cache de embeddings | Por versión de modelo, por contenido hash | Pendiente |

## 10. Riesgos

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Proveedor LLM no disponible en el entorno del workshop | Alto — bloquea Epic 1 y 3 | Tener fallback a modelo local (Ollama) |
| Parsing de lenguaje natural impreciso en español | Medio — UX degradada | Prompt engineering + revisión manual por el usuario (US-002) |
| Embeddings no suficientemente discriminativos para pocas tareas | Medio — RAG irrelevante | Ajustar k y threshold de similaridad |
| Tiempo del workshop insuficiente | Alto — objetivo del curso comprometido | Priorizar Epic 1-2, Epic 3-4 como extensión |
