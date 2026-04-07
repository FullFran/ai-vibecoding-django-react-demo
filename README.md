# ai-vibecoding-django-react-demo

> Repositorio de demostración para el curso **AI Engineering — Piloto Barcelona**.
> Sirve como base sobre la que practicar el framework de trabajo con IA
> (Claude Code, OpenCode y similares) aplicado a un stack real Django + React.

## ¿Qué es esto?

Un mini-proyecto **TaskFlow AI** — gestor de tareas personales con dos giros:

1. **IA procesa las tareas** al crearlas (clasificación, prioridad sugerida, extracción de fechas).
2. **RAG sobre el histórico de tareas** — el usuario puede preguntar en lenguaje natural sobre sus tareas pasadas y el sistema responde con contexto recuperado.

Es **deliberadamente sencillo**. No es un producto, es un campo de pruebas para enseñar el método de trabajo con IA sobre un stack realista.

## Estado del repo

> 🚧 **Solo documentación.** El código todavía no existe. Este repo arranca con specs
> y se irá implementando como parte del propio curso, en vivo o entre sesiones.

## Stack objetivo

| Capa | Tecnología | Notas |
|---|---|---|
| Backend | Django 5 + Django REST Framework | API REST |
| Base de datos | PostgreSQL + pgvector | persistencia + embeddings para RAG |
| Tests backend | pytest + pytest-django | |
| Frontend | React 19 + Vite + TypeScript | SPA |
| Estado | TanStack Query | server state |
| Estilos | Tailwind CSS | |
| Tests frontend | Vitest + React Testing Library | |
| Linter / formatter | Ruff (Python) · ESLint + Prettier (TS) | |
| IA | proveedor agnóstico vía adapter | Anthropic / OpenAI / local |

## Documentación del proyecto

- [`PROJECT_SPECS.md`](./PROJECT_SPECS.md) — descripción funcional, user stories, modelo de datos y reglas de negocio.

## Para qué se usa este repo en el curso

- como **codebase de referencia** sobre la que aplicar el framework agnóstico
- como ejemplo vivo de `CLAUDE.md` / `AGENTS.md` describiendo arquitectura, convenciones y reglas
- como contenedor de **skills custom** del tipo `add-django-endpoint` o `add-react-feature`
- como base para los hands-on de la primera sesión

## Licencia

MIT — ver [LICENSE](./LICENSE).
