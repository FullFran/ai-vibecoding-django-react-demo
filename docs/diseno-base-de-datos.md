# Diseño de base de datos — Sprint 1 MVP sin IA

## 1. Objetivo

Definir el diseño de persistencia para el Sprint 1 del MVP de **AITasks**, limitado al sistema de tareas sin integración de inteligencia artificial.

## 2. Alcance

Este diseño cubre:

- creación, edición, listado y borrado lógico de tareas,
- transición de estados,
- filtros por estado y prioridad,
- paginación de resultados.

Queda fuera de este documento:

- embeddings,
- RAG,
- parsing en lenguaje natural,
- tablas auxiliares de IA.

## 3. Entidad principal

### Tabla: `tasks`

| Campo | Tipo sugerido | Nulo | Descripción |
|---|---|---:|---|
| `id` | UUID | No | Clave primaria de la tarea |
| `title` | varchar(200) | No | Título corto visible en listados |
| `description` | text | Sí | Descripción libre de la tarea |
| `priority` | varchar(10) | No | Valores válidos: `low`, `medium`, `high` |
| `status` | varchar(20) | No | Valores válidos: `TODO`, `IN_PROGRESS`, `DONE` |
| `due_date` | date | Sí | Fecha objetivo opcional |
| `tags` | JSON / array de strings | Sí | Lista simple de etiquetas |
| `created_at` | datetime | No | Fecha de creación |
| `updated_at` | datetime | No | Última modificación |
| `deleted_at` | datetime | Sí | Marca de borrado lógico |

## 4. Reglas de modelado

### 4.1 Clave primaria

- Se recomienda usar UUID para evitar acoplamiento a enteros secuenciales.
- Facilita futura exposición pública de recursos por API.

### 4.2 Campo `title`

- Obligatorio.
- Longitud mínima recomendada: 3 caracteres.
- Longitud máxima: 200 caracteres.

### 4.3 Campo `description`

- Opcional en el MVP.
- Debe permitir texto libre de longitud amplia.

### 4.4 Campo `priority`

- Obligatorio.
- Enum lógico con tres niveles:
  - `low`
  - `medium`
  - `high`
- Valor por defecto: `medium`.

### 4.5 Campo `status`

- Obligatorio.
- Enum lógico con tres estados:
  - `TODO`
  - `IN_PROGRESS`
  - `DONE`
- Valor por defecto al crear: `TODO`.

### 4.6 Campo `due_date`

- Opcional.
- Permite mostrar urgencia y ordenar visualmente en el frontend más adelante.

### 4.7 Campo `tags`

- Opcional.
- Para el MVP basta una lista simple serializable.
- Si el stack final usa PostgreSQL, puede implementarse con `ArrayField` o `JSONField`.
- Si se prioriza portabilidad, conviene `JSONField`.

### 4.8 Campo `deleted_at`

- Implementa **soft delete**.
- Una tarea borrada no debe aparecer en listados normales.
- El registro permanece disponible para histórico y futuras capacidades.

## 5. Restricciones y validaciones

## 5.1 Restricciones funcionales

- `priority` solo admite `low`, `medium`, `high`.
- `status` solo admite `TODO`, `IN_PROGRESS`, `DONE`.
- No se permite crear tareas ya borradas.
- Las tareas con `deleted_at` informado no deben ser editables desde el flujo normal.

## 5.2 Restricciones recomendadas a nivel aplicación

- `title` trimmeado antes de validar.
- `tags` normalizadas sin duplicados exactos.
- `due_date` aceptada solo como fecha válida.

## 6. Índices recomendados

Para el volumen esperado del MVP no hace falta optimización avanzada, pero sí índices básicos:

| Índice | Motivo |
|---|---|
| `created_at` | ordenar listados recientes primero |
| `status` | filtrar por estado |
| `priority` | filtrar por prioridad |
| `deleted_at` | excluir tareas borradas con eficiencia |

Índice compuesto recomendado:

- `deleted_at, created_at`

porque el listado principal probablemente filtrará por no borradas y ordenará por creación descendente.

## 7. Consultas esperadas

### 7.1 Listado principal

- Solo tareas con `deleted_at IS NULL`
- Orden: `created_at DESC`
- Paginación de 20 elementos

### 7.2 Filtros

- por `status`
- por `priority`
- combinables entre sí

### 7.3 Detalle

- por `id`
- solo si `deleted_at IS NULL`

## 8. Decisiones abiertas para implementación

1. **`tags` como JSON vs ArrayField**
   - `JSONField`: más portable.
   - `ArrayField`: más limpio si se fija PostgreSQL.

2. **Base de datos concreta del entorno local**
   - SQLite acelera el arranque.
   - PostgreSQL alinea mejor con un proyecto Django realista.

Para Sprint 1, la opción pragmática es priorizar simplicidad de arranque y mantener el modelo compatible con evolución posterior.

## 9. Modelo conceptual simplificado

```text
Task
 ├── id: UUID
 ├── title: string
 ├── description: text?
 ├── priority: low | medium | high
 ├── status: TODO | IN_PROGRESS | DONE
 ├── due_date: date?
 ├── tags: string[]
 ├── created_at: datetime
 ├── updated_at: datetime
 └── deleted_at: datetime?
```

## 10. Evolución futura prevista

Cuando entre IA en un sprint posterior, este diseño podrá extenderse con:

- tabla `task_embeddings`,
- versionado por modelo de embeddings,
- metadatos de indexación,
- histórico o auditoría si el curso lo requiere.
