---
description: Hacer pull, revisar cambios y crear commits atomicos autoexplicativos
---
# Workflow: Atomic Commits

Objetivo: preparar el branch antes de commitear, detectar conflictos cuanto antes y convertir el trabajo actual en una secuencia de commits pequenos, coherentes y autoexplicativos.

1. Inspecciona el estado actual del repo.
   - Ejecuta `git status --short --branch`.
   - Ejecuta `git log --oneline -5` para ver el estilo reciente de commits.

2. Trae los cambios remotos antes de commitear.
   - Si el arbol de trabajo esta limpio, ejecuta `git pull --rebase`.
   - Si hay cambios locales, ejecuta `git pull --rebase --autostash`.
   - Si aparecen conflictos, DETENTE.
   - Enumera los archivos en conflicto, explica el motivo y no sigas con commits hasta resolverlos.

3. Revisa todo lo que cambiara.
   - Ejecuta `git status --short`.
   - Ejecuta `git diff --staged`.
   - Ejecuta `git diff`.
   - Resume los cambios por intencion, no por archivo: bugfix, refactor, docs, chore, feature, test, etc.

4. Organiza commits atomicos.
   - Agrupa cambios que tengan una sola razon de existir.
   - Separa cambios mecanicos de cambios funcionales.
   - Separa renombres, refactors, docs y fixes cuando puedan vivir por separado.
   - Si un archivo mezcla varios cambios no separables de forma segura sin interaccion, crea el commit minimo seguro y explica esa limitacion.

5. Crea cada commit de forma secuencial.
   - Staging solo del grupo actual.
   - Usa mensajes `conventional commits` claros y autoexplicativos.
   - El mensaje debe explicar por que existe ese commit, no solo que archivos toca.

6. Formato de mensaje recomendado.
   - `feat(area): add natural language task parsing`
   - `fix(api): prevent duplicate task creation on retry`
   - `refactor(tasks): separate parser orchestration from persistence`
   - `docs(workflow): document atomic commit process`

7. Verifica al final.
   - Ejecuta `git status --short --branch`.
   - Confirma cuantos commits se crearon y resume cada uno en una linea.
   - Si quedo trabajo sin commitear, explica por que quedo fuera.

// turbo
Notas para el agente:
- Nunca hagas un commit gigante si puedes separarlo con seguridad.
- Nunca inventes un mensaje generico tipo `update stuff` o `misc fixes`.
- Si el pull introduce conflictos, la prioridad es resolver o escalar ese bloqueo, NO seguir commiteando.
- No hagas push salvo que el usuario lo pida explicitamente.
