# Diseño de endpoints — Sprint 1 MVP sin IA

## 1. Objetivo

Definir la API mínima necesaria para operar el MVP de AITasks sin capacidades de inteligencia artificial.

## 2. Principios del diseño

- API REST simple.
- Recursos centrados en `tasks`.
- Respuestas preparadas para una UI React mínima.
- Exclusión explícita de endpoints de IA en Sprint 1.

## 3. Alcance del Sprint 1

### Incluidos

- listar tareas,
- crear tarea estructurada,
- ver detalle,
- editar,
- borrar lógicamente,
- cambiar estado,
- filtrar,
- paginar.

### Excluidos

- `POST /api/tasks/parse/`
- `POST /api/tasks/ask/`
- `GET /api/tasks/export/` salvo que se priorice después

## 4. Recurso principal

Base path:

```text
/api/tasks/
```

## 5. Contratos de endpoints

### 5.1 Listar tareas

**GET** `/api/tasks/`

#### Query params

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---:|---|
| `status` | string | No | Filtra por `TODO`, `IN_PROGRESS`, `DONE` |
| `priority` | string | No | Filtra por `low`, `medium`, `high` |
| `page` | int | No | Página solicitada |
| `page_size` | int | No | Tamaño de página; por defecto 20 |

#### Reglas

- No devuelve tareas con `deleted_at` informado.
- Orden por `created_at DESC`.
- Los filtros son combinables.

#### Respuesta ejemplo

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "8cb5e8c1-9c67-4d32-8e2d-8c1b4f4f5c0a",
      "title": "Llamar al cliente Pérez",
      "description": "Revisar el presupuesto pendiente",
      "priority": "high",
      "status": "TODO",
      "due_date": "2026-04-10",
      "tags": ["cliente", "ventas"],
      "created_at": "2026-04-09T10:00:00Z",
      "updated_at": "2026-04-09T10:00:00Z"
    }
  ]
}
```

### 5.2 Crear tarea

**POST** `/api/tasks/`

#### Request body

```json
{
  "title": "Preparar propuesta comercial",
  "description": "Incluir costes y cronograma",
  "priority": "medium",
  "due_date": "2026-04-15",
  "tags": ["comercial", "cliente"]
}
```

#### Reglas

- `status` no necesita venir en el body; si no se informa, se crea como `TODO`.
- `priority` por defecto: `medium`.
- `title` es obligatorio.

#### Respuesta esperada

- `201 Created`
- Devuelve la tarea creada.

### 5.3 Ver detalle de tarea

**GET** `/api/tasks/{id}/`

#### Reglas

- Si la tarea no existe o fue borrada lógicamente, responde `404`.

### 5.4 Editar tarea

**PATCH** `/api/tasks/{id}/`

#### Request body ejemplo

```json
{
  "title": "Preparar propuesta comercial final",
  "priority": "high",
  "due_date": "2026-04-14"
}
```

#### Reglas

- Solo actualiza campos enviados.
- No permite modificar `id`, `created_at`, `deleted_at`.
- No permite editar tareas borradas.

### 5.5 Borrado lógico

**DELETE** `/api/tasks/{id}/`

#### Reglas

- No elimina físicamente la fila.
- Asigna valor a `deleted_at`.
- Respuesta recomendada: `204 No Content`.

### 5.6 Transición de estado

**POST** `/api/tasks/{id}/transition/`

#### Request body ejemplo

```json
{
  "direction": "forward"
}
```

o

```json
{
  "direction": "backward"
}
```

#### Reglas

- Valores permitidos para `direction`:
  - `forward`
  - `backward`
- Solo se puede avanzar o retroceder **un paso por vez**.

#### Matriz de transición

| Estado actual | `forward` | `backward` |
|---|---|---|
| `TODO` | `IN_PROGRESS` | no permitido |
| `IN_PROGRESS` | `DONE` | `TODO` |
| `DONE` | no permitido | `IN_PROGRESS` |

#### Respuestas de error esperadas

- `400 Bad Request` si la transición es inválida.
- `404 Not Found` si la tarea no existe o está borrada.

## 6. Esquema de errores recomendado

Formato consistente:

```json
{
  "error": {
    "code": "validation_error",
    "message": "priority must be one of: low, medium, high",
    "details": {
      "priority": ["invalid value"]
    }
  }
}
```

## 7. Validaciones por endpoint

### Crear / Editar

- `title` obligatorio al crear
- `title` entre 3 y 200 caracteres
- `priority` dentro de enum válido
- `status` dentro de enum válido si se expone para edición futura
- `due_date` con formato de fecha válido
- `tags` como lista de strings

### Transition

- `direction` obligatorio
- no permitir saltos directos de `TODO` a `DONE`
- no permitir retroceso desde `TODO`
- no permitir avance desde `DONE`

## 8. Endpoints no implementados en Sprint 1

Se mantienen documentados en el PRD, pero fuera del corte inicial:

- `POST /api/tasks/parse/`
- `POST /api/tasks/ask/`
- `GET /api/tasks/export/`

Esto evita mezclar el MVP de tareas con la capa de IA antes de tener la base funcional estable.
