# Proposal — sprint1-mvp-tasks

**Change**: Sprint 1 MVP — Task Management Backend  
**Status**: proposed  
**Date**: 2026-04-09  
**Author**: SDD Proposal Agent

---

## 1. Intent

Build the foundational Django backend for AITasks: a fully functional REST API that supports CRUD operations on tasks, state transitions, filtering, pagination, and soft delete. This is Sprint 1 — no AI, no embeddings, no frontend. The goal is a rock-solid backend that future sprints (AI parsing, RAG, React UI) can build on without rework.

**Why now**: The course needs a working codebase to demonstrate AI-assisted development workflows. Without a stable backend, nothing else moves forward.

## 2. Scope

### In scope

- Django project scaffolding (`aitasks` project, `tasks` app)
- `Task` model with UUID PK, soft delete, state machine, tags
- Django REST Framework API: list, create, detail, update, soft delete, state transition
- Filtering by status and priority (django-filter)
- Cursor-free page-number pagination (20 per page)
- Input validation (title length, enum constraints, date format, tag dedup)
- Database indices per spec
- Test suite covering all endpoints and business rules
- Development configuration (settings, URLs, requirements)

### Out of scope

- React frontend (deferred to Sprint 2+)
- AI parsing (`/api/tasks/parse/`)
- RAG / embeddings (`/api/tasks/ask/`, `TaskEmbedding` model)
- JSON export (`/api/tasks/export/`)
- Authentication / authorization
- Docker / deployment configuration
- CI/CD pipeline

## 3. Approach

### 3.1 Project structure

Standard Django layout, single app for Sprint 1:

```
repo-demo/
├── manage.py
├── requirements.txt
├── aitasks/                  # Django project
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── tasks/                    # Django app
    ├── __init__.py
    ├── models.py             # Task model
    ├── serializers.py        # DRF serializers
    ├── views.py              # ViewSet
    ├── urls.py               # Router config
    ├── filters.py            # django-filter FilterSet
    ├── services.py           # State transition logic
    ├── managers.py           # Custom queryset (alive-only default)
    ├── admin.py              # Basic admin registration
    ├── migrations/
    └── tests/
        ├── __init__.py
        ├── test_models.py
        ├── test_serializers.py
        ├── test_views.py
        └── test_services.py
```

### 3.2 Key decision: SQLite (not PostgreSQL)

**Decision**: SQLite for Sprint 1 local development.

**Rationale**:
- Zero setup friction — critical for a course environment where participants need to get running fast.
- Django's ORM abstracts the difference; migrating to PostgreSQL later is a settings change + re-migrate.
- The data volume is trivial (<1000 tasks). No PostgreSQL-specific features are needed in Sprint 1.
- `JSONField` works on SQLite since Django 3.1.

**Tradeoff accepted**: No `ArrayField`. Tags use `JSONField` instead (see 3.3).

### 3.3 Key decision: JSONField for tags (not ArrayField)

**Decision**: `models.JSONField(default=list, blank=True)`.

**Rationale**:
- `ArrayField` is PostgreSQL-only. Using `JSONField` keeps the project database-agnostic.
- Validation of the JSON structure (list of strings) happens at the serializer level.
- If the project migrates to PostgreSQL later, this field can stay as-is or be swapped — neither path requires data migration.

### 3.4 Key decision: Backend-only for Sprint 1

**Decision**: No React frontend in Sprint 1.

**Rationale**:
- The docs explicitly separate frontend user stories from API contracts.
- DRF's browsable API is sufficient for manual testing and course demonstrations.
- Shipping a half-baked frontend creates more confusion than shipping no frontend.
- Frontend becomes Sprint 2, where participants can practice AI-assisted React generation against a stable API.

### 3.5 Model design

Single `Task` model following `docs/diseno-base-de-datos.md` exactly:

- `id`: `UUIDField(primary_key=True, default=uuid.uuid4, editable=False)`
- `title`: `CharField(max_length=200)` — validated min 3 chars at serializer level
- `description`: `TextField(blank=True, default="")`
- `priority`: `CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")`
- `status`: `CharField(max_length=20, choices=STATUS_CHOICES, default="TODO")`
- `due_date`: `DateField(null=True, blank=True)`
- `tags`: `JSONField(default=list, blank=True)`
- `created_at`: `DateTimeField(auto_now_add=True)`
- `updated_at`: `DateTimeField(auto_now=True)`
- `deleted_at`: `DateTimeField(null=True, blank=True)`

Custom manager `AliveManager` as default: filters `deleted_at__isnull=True`. Second manager `all_objects` for unfiltered access.

Indices: `created_at`, `status`, `priority`, `deleted_at`, composite `(deleted_at, created_at)`.

### 3.6 API design

DRF `ModelViewSet` with custom actions:

| Method | Path | Action | Notes |
|--------|------|--------|-------|
| GET | `/api/tasks/` | list | Paginated, filtered, excludes soft-deleted |
| POST | `/api/tasks/` | create | Title required, defaults applied |
| GET | `/api/tasks/{id}/` | retrieve | 404 if soft-deleted |
| PATCH | `/api/tasks/{id}/` | partial_update | Rejects edits on deleted tasks |
| DELETE | `/api/tasks/{id}/` | destroy (soft) | Sets `deleted_at`, returns 204 |
| POST | `/api/tasks/{id}/transition/` | transition | Custom action, validates state machine |

### 3.7 Business logic placement

Following Django best practice ("thin views, fat models/services"):

- **State machine** lives in `tasks/services.py` — a pure function `transition_status(current_status, direction) -> new_status` that raises `ValidationError` on invalid transitions. Easily testable in isolation.
- **Soft delete** logic in a custom manager (`tasks/managers.py`) — the default queryset excludes deleted tasks. The `destroy` method on the viewset sets `deleted_at` instead of calling `.delete()`.
- **Validation** (title trim, tag dedup, date checks) in the serializer's `validate_*` methods.

### 3.8 Dependencies

```
django>=5.1,<5.2
djangorestframework>=3.15,<4.0
django-filter>=24.0,<25.0
```

Minimal. No extra libraries. DRF covers serialization, pagination, and the browsable API. django-filter handles query param filtering cleanly.

### 3.9 Error response format

DRF's default error format is close to the spec in `docs/diseno-endpoints.md`. We will use a custom exception handler to wrap errors in the `{"error": {"code": ..., "message": ..., "details": ...}}` envelope documented in the endpoint spec.

### 3.10 Pagination

DRF `PageNumberPagination` subclass with `page_size=20` and `page_size_query_param="page_size"`. Response shape matches the spec: `count`, `next`, `previous`, `results`.

## 4. Affected modules

| Module | Action | Description |
|--------|--------|-------------|
| `aitasks/` | CREATE | Django project package (settings, urls, wsgi) |
| `tasks/` | CREATE | Django app (models, views, serializers, services, managers, filters, tests) |
| `manage.py` | CREATE | Django management script |
| `requirements.txt` | CREATE | Python dependencies |

No existing code is modified — this is a greenfield implementation.

## 5. Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| SQLite limitations surface later (concurrent writes, missing features) | Low | Medium | Django ORM abstracts DB; migration to PostgreSQL is a settings swap + `migrate`. No PostgreSQL-specific features used. |
| JSONField validation gaps (non-string items in tags array) | Medium | Low | Serializer-level validation: reject any tag that is not a string. Add explicit test cases. |
| Scope creep into AI features | Medium | High | Hard boundary: no `/parse/`, `/ask/`, or `TaskEmbedding` in Sprint 1. Endpoints return 404 if accidentally hit. |
| Custom error format diverges from DRF conventions | Low | Low | Custom exception handler tested explicitly. Keep it thin — just reshape, don't add logic. |
| State transition race conditions | Low | Low | Single-user MVP, no concurrent access expected. Document that production use would need `select_for_update()`. |

## 6. Rollback plan

This is a greenfield change on an empty repo (no existing code). Rollback is trivial:

1. `git revert` any implementation commits — returns to docs-only state.
2. No database to migrate down (SQLite file can be deleted).
3. No external services or infrastructure to tear down.

If a partial rollback is needed (e.g., model is fine but views need rework), individual commits can be reverted since the implementation will follow the task breakdown (model first, then serializers, then views, then tests).

## 7. Implementation order (preview)

This will be detailed in the tasks phase, but the dependency chain is:

1. Project scaffolding (django-admin startproject, startapp, settings, requirements)
2. Task model + managers + migration
3. Serializers + validation
4. State transition service
5. ViewSet + URL routing + filters + pagination + custom error handler
6. Test suite (models, serializers, services, views)

Each step is independently committable and testable.
