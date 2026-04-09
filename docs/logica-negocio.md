# Lógica de negocio — Sprint 1 MVP sin IA

## 1. Objetivo

Registrar las reglas de negocio y comportamientos funcionales del MVP de AITasks en su primer sprint, limitado a la gestión manual de tareas.

## 2. Principio de recorte funcional

El PRD original describe un producto con IA, pero el Sprint 1 se centra en una base funcional sólida.

Por tanto:

- la creación de tareas será manual,
- no existirá parsing en lenguaje natural,
- no existirán embeddings ni RAG,
- las reglas documentadas aquí solo cubren el sistema de tareas clásico.

## 3. Reglas principales

### 3.1 Creación de tareas

- Una tarea debe tener `title`.
- `description` puede estar vacía.
- Si no se informa `priority`, se asigna `medium`.
- Toda tarea nueva nace en estado `TODO`.
- `due_date` es opcional.
- `tags` es opcional.

### 3.2 Visibilidad

- Solo se muestran en listados las tareas no borradas lógicamente.
- Si no hay tareas visibles, la UI debe mostrar un estado vacío claro: **"No hay tareas"**.

### 3.3 Orden de listado

- El listado principal muestra las tareas más recientes primero.
- El criterio base es `created_at DESC`.

### 3.4 Paginación

- El listado se pagina de 20 en 20.
- La paginación debe mantenerse al navegar por filtros y listados.

### 3.5 Edición

- Una tarea puede editarse mientras no esté borrada.
- La edición actualiza `updated_at`.
- La edición no debe cambiar `created_at`.

### 3.6 Borrado lógico

- El borrado de una tarea es lógico, no físico.
- Al borrar, se informa `deleted_at`.
- Una tarea borrada deja de aparecer en la UI normal.
- El mantenimiento del registro permite evolución futura del histórico.

### 3.7 Transición de estados

Estados válidos:

- `TODO`
- `IN_PROGRESS`
- `DONE`

Regla central:

- solo se puede avanzar o retroceder **un paso por vez**.

Transiciones válidas:

- `TODO -> IN_PROGRESS`
- `IN_PROGRESS -> DONE`
- `IN_PROGRESS -> TODO`
- `DONE -> IN_PROGRESS`

Transiciones inválidas:

- `TODO -> DONE`
- `DONE -> TODO`
- cualquier transición sobre una tarea borrada

### 3.8 Filtros

- El usuario puede filtrar por estado.
- El usuario puede filtrar por prioridad.
- Ambos filtros deben poder combinarse.
- El filtro actual debe mantenerse tras crear o editar una tarea, siempre que la tarea siga cumpliendo el criterio visible en pantalla.

## 4. Historias funcionales reinterpretadas para el MVP

## 4.1 US-001 — Ver lista de tareas

Se mantiene prácticamente igual:

- estado vacío inicial,
- visualización de título, prioridad, estado y fecha objetivo,
- orden por recientes,
- paginación.

## 4.2 US-002A — Crear tarea manual

Esta historia reemplaza temporalmente la creación en lenguaje natural.

### Criterios de aceptación

- El usuario dispone de un formulario manual.
- Puede completar `title`, `description`, `priority`, `due_date` y `tags`.
- Al confirmar, la tarea se guarda sin pasos de IA.
- La tarea aparece en el listado.

## 4.3 US-003 — Editar tarea

Se mantiene:

- formulario con datos actuales,
- guardar o cancelar,
- actualización persistida.

## 4.4 US-004 — Eliminar tarea

Se mantiene con soft delete:

- confirmación previa,
- ocultación en listados,
- persistencia física del registro.

## 4.5 US-005 — Cambiar estado

Se mantiene:

- botón o acción visible para avanzar o retroceder,
- respeto de las transiciones válidas,
- reflejo inmediato en la UI.

## 4.6 US-006 — Filtrar por estado y prioridad

Se mantiene:

- tabs de estado,
- filtro adicional por prioridad,
- persistencia del criterio actual mientras el usuario trabaja.

## 5. Casos borde importantes

1. **Crear sin prioridad**
   - resultado: se asigna `medium`.

2. **Editar una tarea borrada**
   - resultado: operación rechazada.

3. **Cambiar estado de `DONE` hacia adelante**
   - resultado: operación inválida.

4. **Cambiar estado de `TODO` hacia atrás**
   - resultado: operación inválida.

5. **Filtros activos al crear**
   - si la nueva tarea no cumple el filtro actual, puede no verse en la lista filtrada; esto NO es error funcional.

## 6. Decisiones funcionales explícitas del Sprint 1

### 6.1 No incluir IA todavía

Razón:

- primero hay que estabilizar el dominio base,
- el flujo manual permite validar modelo, API y UI,
- reduce riesgo y tiempo de arranque del curso.

### 6.2 Mantener soft delete aunque aún no haya RAG

Razón:

- preserva coherencia con el PRD,
- evita rediseño posterior,
- deja preparado el histórico para una fase futura.

### 6.3 Mantener `tags` aunque el MVP sea simple

Razón:

- ya forman parte del modelo objetivo,
- su coste de incorporación es bajo,
- preparan el terreno para búsqueda y clasificación posterior.

## 7. Riesgos funcionales del sprint

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Intentar meter IA demasiado pronto | Alto | congelar explícitamente endpoints y features fuera del MVP |
| Sobrediseñar el modelo para el futuro | Medio | mantener una sola entidad principal en Sprint 1 |
| Inconsistencias entre filtros y UI | Medio | fijar contratos claros en API y frontend |

## 8. Resultado esperado del Sprint 1

Al cerrar el sprint, el usuario debe poder:

1. crear tareas manualmente,
2. listarlas,
3. editarlas,
4. borrarlas lógicamente,
5. moverlas entre estados válidos,
6. filtrarlas por estado y prioridad.

Si eso funciona de punta a punta, el MVP base está logrado.
