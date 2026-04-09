# Tasks — sprint1-mvp-tasks

**Change**: Sprint 1 MVP — Task Management Backend
**Status**: pending
**Date**: 2026-04-09
**Author**: SDD Tasks Agent

---

## Overview

22 implementation tasks grouped into 5 phases. All tasks are ordered by dependency; earlier tasks are prerequisites for later ones. Each task is independently committable and references specific spec requirements (REQ-*) and design sections.

---

## Phase 1: Infrastructure

### Task 1.1 — Create Django project and app scaffolding

**Description**: Initialize the Django project package (`aitasks/`) and the tasks Django app (`tasks/`) with all required `__init__.py` files and `apps.py`. Also create `manage.py` at repo root. Do NOT configure settings yet — that is task 1.3. Do NOT write any business logic.

**Spec refs**: None directly (structural prerequisite for all REQ-*)

**Design refs**: Design §1.1 Component Diagram

**Acceptance criteria**:
- `manage.py` exists at repo root and is executable
- `aitasks/__init__.py` and `aitasks/wsgi.py` exist
- `tasks/__init__.py`, `tasks/apps.py` exist
- `tasks/migrations/__init__.py` exists
- `tasks/tests/__init__.py` exists
- Running `python manage.py check` succeeds (after settings are configured in 1.3)

**Dependencies**: none

**Files**:
- `manage.py` (create)
- `aitasks/__init__.py` (create)
- `aitasks/wsgi.py` (create)
- `tasks/__init__.py` (create)
- `tasks/apps.py` (create)
- `tasks/migrations/__init__.py` (create)
- `tasks/tests/__init__.py` (create)

**Status**: pending

---

### Task 1.2 — Create requirements.txt with pinned dependencies

**Description**: Create `requirements.txt` at repo root with all pinned Python dependencies needed for Sprint 1: Django, djangorestframework, django-filter. Pin exact versions to ensure reproducible builds.

**Spec refs**: REQ-F-001 (django-filter required for filtering)

**Design refs**: Design §1.1 Component Diagram (`requirements.txt` node)

**Acceptance criteria**:
- `requirements.txt` exists at repo root
- Includes `Django>=4.2,<5.1` (or pinned), `djangorestframework>=3.14`, `django-filter>=23.0`
- `pip install -r requirements.txt` completes without errors

**Dependencies**: none (can be done in parallel with 1.1)

**Files**:
- `requirements.txt` (create)

**Status**: pending

---

### Task 1.3 — Configure settings.py

**Description**: Create `aitasks/settings.py` with full Django configuration: `INSTALLED_APPS` including `rest_framework`, `django_filters`, and `tasks`; `REST_FRAMEWORK` dict with `EXCEPTION_HANDLER`, `DEFAULT_FILTER_BACKENDS`; `DEFAULT_AUTO_FIELD`; `DATABASES` using SQLite for development; all standard Django middleware.

**Spec refs**: REQ-E-005 (custom exception handler must be registered); REQ-F-001 (django-filter backend)

**Design refs**: Design §3 Settings Configuration

**Acceptance criteria**:
- `aitasks/settings.py` exists
- `INSTALLED_APPS` contains `"rest_framework"`, `"django_filters"`, `"tasks"`
- `REST_FRAMEWORK["EXCEPTION_HANDLER"]` = `"aitasks.exceptions.custom_exception_handler"`
- `REST_FRAMEWORK["DEFAULT_FILTER_BACKENDS"]` includes DjangoFilterBackend
- `DEFAULT_AUTO_FIELD` = `"django.db.models.BigAutoField"`
- `python manage.py check` passes with no errors

**Dependencies**: 1.1

**Files**:
- `aitasks/settings.py` (create)

**Status**: pending

---

### Task 1.4 — Set up root URL configuration

**Description**: Create `aitasks/urls.py` as the root URL conf. Wire up Django admin at `/admin/` and include `tasks.urls` at `/api/`. This wires up all task endpoints under `/api/tasks/`.

**Spec refs**: REQ-C-001 (`POST /api/tasks/`); REQ-L-001 (`GET /api/tasks/`); REQ-T-001 (`POST /api/tasks/{id}/transition/`)

**Design refs**: Design §2.7 urls.py (root urlconf block)

**Acceptance criteria**:
- `aitasks/urls.py` exists with `urlpatterns` that includes `"admin/"` and `"api/"` paths
- `ROOT_URLCONF` in settings.py points to `"aitasks.urls"`
- `python manage.py check --deploy` passes (warnings OK, errors not)

**Dependencies**: 1.3

**Files**:
- `aitasks/urls.py` (create)
- `aitasks/settings.py` (modify: add `ROOT_URLCONF`)

**Status**: pending

---

## Phase 2: Core Implementation

### Task 2.1 — Implement tasks/managers.py (AliveManager)

**Description**: Create `tasks/managers.py` with the `AliveManager` class. It extends `models.Manager` and overrides `get_queryset()` to filter `deleted_at__isnull=True`. This is the default manager used by all standard ORM queries.

**Spec refs**: REQ-M-011 (default manager excludes soft-deleted; `all_objects` manager for all rows)

**Design refs**: Design §2.2 managers.py

**Acceptance criteria**:
- `AliveManager.get_queryset()` returns only rows where `deleted_at IS NULL`
- The class has no other methods
- File has no imports beyond `from django.db import models`

**Dependencies**: 1.1

**Files**:
- `tasks/managers.py` (create)

**Status**: pending

---

### Task 2.2 — Implement tasks/models.py (Task model)

**Description**: Create `tasks/models.py` with `PRIORITY_CHOICES`, `STATUS_CHOICES` constants, and the `Task` model. Fields: `id` (UUIDField PK, auto-generated), `title` (CharField max_length=200), `description` (TextField, blank, default=""), `priority` (CharField with choices, default="medium"), `status` (CharField with choices, default="TODO"), `due_date` (DateField, null, blank), `tags` (JSONField, default=list), `created_at` (DateTimeField auto_now_add), `updated_at` (DateTimeField auto_now), `deleted_at` (DateTimeField null, blank). Managers: `objects = AliveManager()`, `all_objects = models.Manager()`. Meta: `ordering = ["-created_at"]`, all required indexes.

**Spec refs**: REQ-M-001 through REQ-M-012

**Design refs**: Design §2.1 models.py

**Acceptance criteria**:
- All 10 fields present with correct types, nullability, defaults
- `objects` is `AliveManager` instance (default manager)
- `all_objects` is plain `models.Manager()` instance
- `Meta.ordering = ["-created_at"]`
- `Meta.indexes` contains 5 index definitions: `created_at`, `status`, `priority`, `deleted_at`, and composite `(deleted_at, created_at)`
- `__str__` returns `self.title`

**Dependencies**: 2.1

**Files**:
- `tasks/models.py` (create)

**Status**: pending

---

### Task 2.3 — Generate and verify initial migration

**Description**: Run `python manage.py makemigrations tasks` to generate `tasks/migrations/0001_initial.py`. Inspect the generated migration to verify all fields, indexes, and choices are correct. Do NOT manually edit the migration file.

**Spec refs**: REQ-M-001 through REQ-M-012 (all model requirements reflected in DB schema)

**Design refs**: Design §1.1 (migrations/ directory)

**Acceptance criteria**:
- `tasks/migrations/0001_initial.py` exists and is auto-generated
- Migration contains `UUIDField` for `id` with `primary_key=True`
- Migration contains all 5 index definitions
- `python manage.py migrate` completes with no errors
- `python manage.py sqlmigrate tasks 0001` shows correct SQL

**Dependencies**: 2.2

**Files**:
- `tasks/migrations/0001_initial.py` (create via `makemigrations`)

**Status**: pending

---

### Task 2.4 — Implement tasks/serializers.py

**Description**: Create `tasks/serializers.py` with two serializers:

1. `TaskSerializer(ModelSerializer)`: fields `["id", "title", "description", "priority", "status", "due_date", "tags", "created_at", "updated_at"]` (no `deleted_at`), `read_only_fields = ["id", "status", "created_at", "updated_at"]`. Custom `validate_title`: strip whitespace, enforce 3–200 chars. Custom `validate_tags`: ensure list of strings, dedup with `dict.fromkeys()`.

2. `TransitionSerializer(Serializer)`: single `direction` ChoiceField with choices `[("forward", "Forward"), ("backward", "Backward")]`.

**Spec refs**: REQ-C-002 through REQ-C-011; REQ-U-001 through REQ-U-008; REQ-V-001 through REQ-V-008; REQ-E-001

**Design refs**: Design §2.3 serializers.py; ADR-001; ADR-005

**Acceptance criteria**:
- `deleted_at` is NOT in `TaskSerializer.Meta.fields`
- `status` is in `read_only_fields` (silently ignored on write)
- `validate_title` strips whitespace BEFORE length check, raises `ValidationError` if < 3 or > 200
- `validate_tags` raises `ValidationError` if not a list or any element is not a string
- `validate_tags` deduplicates preserving insertion order
- `TransitionSerializer.direction` is a `ChoiceField` with only `"forward"` and `"backward"`

**Dependencies**: 2.2

**Files**:
- `tasks/serializers.py` (create)

**Status**: pending

---

### Task 2.5 — Implement tasks/services.py (transition_status)

**Description**: Create `tasks/services.py` with the `TRANSITION_MATRIX` dict constant and the `transition_status(current_status, direction)` pure function. The function looks up `(current_status, direction)` in the matrix; if found, returns the new status string; if not found, raises `ValidationError` with `code="invalid_transition"` and a `details` dict keyed by `"direction"`.

**Spec refs**: REQ-T-004 (transition matrix); REQ-T-005 (invalid transitions return 400); REQ-T-008 (logic in services.py); REQ-E-002 (`invalid_transition` code)

**Design refs**: Design §2.4 services.py; ADR-002

**Acceptance criteria**:
- `TRANSITION_MATRIX` has exactly 4 valid entries: `(TODO, forward)→IN_PROGRESS`, `(IN_PROGRESS, forward)→DONE`, `(IN_PROGRESS, backward)→TODO`, `(DONE, backward)→IN_PROGRESS`
- `transition_status("TODO", "forward")` returns `"IN_PROGRESS"`
- `transition_status("DONE", "forward")` raises `ValidationError` with `code="invalid_transition"`
- `transition_status("TODO", "backward")` raises `ValidationError` with `code="invalid_transition"`
- Function has no database access, no side effects (pure function)

**Dependencies**: 1.1 (package structure only; no model import needed)

**Files**:
- `tasks/services.py` (create)

**Status**: pending

---

## Phase 3: API Layer

### Task 3.1 — Implement aitasks/exceptions.py (custom exception handler)

**Description**: Create `aitasks/exceptions.py` with the `custom_exception_handler(exc, context)` function. It must: (1) call DRF's built-in `exception_handler` first, (2) if response is None, return None, (3) reshape the response data into `{"error": {"code": str, "message": str, "details": dict|None}}`, (4) map DRF internal codes to API codes (`not_found`, `validation_error`, `invalid_transition`), (5) detect `invalid_transition` code from `ValidationError` and preserve it.

**Spec refs**: REQ-E-001 through REQ-E-006

**Design refs**: Design §2.8 exceptions.py; ADR-004

**Acceptance criteria**:
- 404 responses produce `{"error": {"code": "not_found", "message": "..."}}`
- Validation errors produce `{"error": {"code": "validation_error", "message": "...", "details": {"field": ["..."]}}}`
- `invalid_transition` ValidationErrors produce `{"error": {"code": "invalid_transition", "message": "..."}}`
- Handler calls DRF's `exception_handler` first (no behavior override, only reshaping)
- No business logic in the handler

**Dependencies**: 1.3 (settings must reference this handler)

**Files**:
- `aitasks/exceptions.py` (create)

**Status**: pending

---

### Task 3.2 — Implement tasks/filters.py (TaskFilter)

**Description**: Create `tasks/filters.py` with `TaskFilter(django_filters.FilterSet)`. Fields: `status` as `ChoiceFilter(choices=STATUS_CHOICES)`, `priority` as `ChoiceFilter(choices=PRIORITY_CHOICES)`. Override the `qs` property to call `self.is_valid()` and raise `rest_framework.exceptions.ValidationError` with `self.errors` if the filter form is invalid — this converts invalid filter params into 400 responses through the custom exception handler.

**Spec refs**: REQ-F-001 through REQ-F-005; REQ-L-006 through REQ-L-010

**Design refs**: Design §2.6 filters.py (including the strict mode override block)

**Acceptance criteria**:
- `TaskFilter` has `status` and `priority` ChoiceFilter fields
- `Meta.model = Task`, `Meta.fields = ["status", "priority"]`
- Filtering with `status=TODO` returns only TODO tasks
- Filtering with `status=FINISHED` raises `ValidationError` (returns 400)
- Filtering with `priority=critical` raises `ValidationError` (returns 400)
- Both filters can be applied simultaneously (AND semantics)

**Dependencies**: 2.2

**Files**:
- `tasks/filters.py` (create)

**Status**: pending

---

### Task 3.3 — Implement tasks/views.py (TaskViewSet)

**Description**: Create `tasks/views.py` with `TaskPagination(PageNumberPagination)` (page_size=20, page_size_query_param="page_size") and `TaskViewSet(ModelViewSet)`. ViewSet config: `queryset = Task.objects.all()`, `serializer_class = TaskSerializer`, `pagination_class = TaskPagination`, `filter_backends = [DjangoFilterBackend]`, `filterset_class = TaskFilter`, `http_method_names = ["get", "post", "patch", "delete", "head", "options"]` (PUT excluded). Override `destroy()` for soft delete (set `deleted_at = timezone.now()`, save with `update_fields`). Add `transition()` action with `@action(detail=True, methods=["post"], url_path="transition")`.

**Spec refs**: REQ-C-001/009 (create + 201); REQ-L-001 through REQ-L-010 (list + pagination + filtering); REQ-D-001 through REQ-D-004 (detail); REQ-U-001 through REQ-U-008 (update); REQ-SD-001 through REQ-SD-006 (soft delete); REQ-T-001 through REQ-T-009 (transition)

**Design refs**: Design §2.5 views.py; §1.3 sequence diagrams; ADR-003

**Acceptance criteria**:
- `PUT` method is NOT in `http_method_names`
- `destroy()` sets `deleted_at` and calls `save(update_fields=["deleted_at", "updated_at"])` — does NOT call `super().destroy()`
- `destroy()` returns `Response(status=HTTP_204_NO_CONTENT)`
- `transition()` is decorated with `@action(detail=True, methods=["post"], url_path="transition")`
- `transition()` uses `get_object()` (respects AliveManager — returns 404 for soft-deleted)
- `transition()` calls `TransitionSerializer` for direction validation, then `transition_status()` from services
- `transition()` returns `TaskSerializer(task).data` with status 200

**Dependencies**: 2.4, 2.5, 3.1, 3.2

**Files**:
- `tasks/views.py` (create)

**Status**: pending

---

### Task 3.4 — Implement tasks/urls.py (Router registration)

**Description**: Create `tasks/urls.py`. Instantiate `DefaultRouter()`, register `TaskViewSet` at prefix `"tasks"` with `basename="task"`. Export `urlpatterns = [path("", include(router.urls))]`. This generates the standard CRUD URLs plus the `transition` action URL.

**Spec refs**: REQ-C-001 (`/api/tasks/`); REQ-T-001 (`/api/tasks/{id}/transition/`)

**Design refs**: Design §2.7 urls.py (tasks app section)

**Acceptance criteria**:
- `DefaultRouter` is used (not `SimpleRouter`) so the API root is browsable
- `TaskViewSet` is registered with `basename="task"`
- URL patterns generated: `GET/POST /api/tasks/`, `GET/PATCH/DELETE /api/tasks/{pk}/`, `POST /api/tasks/{pk}/transition/`

**Dependencies**: 3.3

**Files**:
- `tasks/urls.py` (create)

**Status**: pending

---

### Task 3.5 — Wire root URLs to include tasks.urls under /api/

**Description**: Update `aitasks/urls.py` (created in 1.4) to include `"tasks.urls"` under the path prefix `"api/"`. Ensure `path("admin/", admin.site.urls)` is also present.

**Spec refs**: REQ-C-001 (`POST /api/tasks/`); REQ-L-001 (`GET /api/tasks/`); REQ-T-001 (`POST /api/tasks/{id}/transition/`)

**Design refs**: Design §2.7 urls.py (root urlconf block)

**Acceptance criteria**:
- `aitasks/urls.py` includes `path("api/", include("tasks.urls"))`
- `python manage.py show_urls` (or equivalent) lists all expected endpoints
- `python manage.py check` still passes

**Dependencies**: 1.4, 3.4

**Files**:
- `aitasks/urls.py` (modify)

**Status**: pending

---

### Task 3.6 — Register Task in admin.py

**Description**: Create `tasks/admin.py` with a basic `ModelAdmin` registration for the `Task` model. Use `Task.all_objects` as the queryset source so soft-deleted tasks are visible in Django admin.

**Spec refs**: None (not a Sprint 1 API requirement; admin is infrastructure)

**Design refs**: Design §1.1 (admin.py node); ADR-003 (note about admin and AliveManager)

**Acceptance criteria**:
- `tasks/admin.py` exists and registers `Task` with `admin.site.register`
- Admin is accessible at `/admin/` with no import errors
- `python manage.py check` passes

**Dependencies**: 2.3 (migration must exist for admin to work)

**Files**:
- `tasks/admin.py` (create)

**Status**: pending

---

## Phase 4: Testing

### Task 4.1 — Implement tasks/tests/test_models.py

**Description**: Write unit tests for the `Task` model covering: UUID auto-generation (M-01), default values on creation (M-02), AliveManager excludes soft-deleted (M-03), `all_objects` includes soft-deleted (M-04), tags deduplication at model level (M-05). Use Django's `TestCase`. No HTTP layer — direct ORM only.

**Spec refs**: REQ-M-001 through REQ-M-011; Scenarios M-01 through M-05

**Design refs**: Design §2.1 models.py; §2.2 managers.py

**Acceptance criteria**:
- All 5 model scenarios have corresponding test methods
- Tests use `TestCase` (not `APITestCase`)
- No mocking of the database — real SQLite in test mode
- `python manage.py test tasks.tests.test_models` passes with all tests green

**Dependencies**: 2.3

**Files**:
- `tasks/tests/test_models.py` (create)

**Status**: pending

---

### Task 4.2 — Implement tasks/tests/test_serializers.py

**Description**: Write unit tests for `TaskSerializer` and `TransitionSerializer` covering: title trim/length validation (V-01 through V-04, V-07 trim-reduces-below-min), tags type check and dedup (V-05 through V-08), priority enum validation, read-only fields (`id`, `status`, `created_at`, `updated_at` are ignored on write), `deleted_at` absent from output. Test `TransitionSerializer` for valid/invalid direction values.

**Spec refs**: REQ-V-001 through REQ-V-008; REQ-C-005/010/011; REQ-U-003/004; Scenarios V-01 through V-08

**Design refs**: Design §2.3 serializers.py; ADR-001; ADR-005

**Acceptance criteria**:
- Tests instantiate serializers directly (no HTTP requests)
- `validate_title` is tested with: exact 3-char, exact 200-char, 2-char (fail), 201-char (fail), whitespace-only (fail), " ab " (trimmed to "ab" → fail)
- `validate_tags` is tested with: non-list (fail), list with int element (fail), list with bool element (fail), valid list, list with duplicates (deduped)
- `read_only_fields` test verifies that writing `status="DONE"` in serializer data results in `TODO` in output
- `python manage.py test tasks.tests.test_serializers` passes

**Dependencies**: 2.4

**Files**:
- `tasks/tests/test_serializers.py` (create)

**Status**: pending

---

### Task 4.3 — Implement tasks/tests/test_services.py

**Description**: Write unit tests for `transition_status()` covering all 6 cells of the matrix (4 valid + 2 invalid) and any edge cases. These are pure function tests — no database, no HTTP, no fixtures. Use `unittest.TestCase` or Django's `SimpleTestCase`.

**Spec refs**: REQ-T-004; REQ-T-005; Scenarios T-01 through T-06; REQ-T-008

**Design refs**: Design §2.4 services.py; ADR-002

**Acceptance criteria**:
- 4 tests for valid transitions, each asserting the returned string
- 2 tests for invalid transitions, each asserting `ValidationError` is raised with `code="invalid_transition"`
- No database access in any test method
- `python manage.py test tasks.tests.test_services` passes

**Dependencies**: 2.5

**Files**:
- `tasks/tests/test_services.py` (create)

**Status**: pending

---

### Task 4.4 — Implement tasks/tests/test_views.py

**Description**: Write integration tests for all API endpoints using DRF's `APITestCase` and `APIClient`. Cover every scenario from spec sections 2–8:

- **Create** (POST /api/tasks/): happy path, missing title, short title, whitespace title, long title, invalid priority, invalid due_date, non-string tag, duplicate tags deduped, status field ignored
- **List** (GET /api/tasks/): excludes soft-deleted, ordered newest-first, pagination default size 20, second page, empty list 200, filter by status, filter by priority, combined filter, custom page_size, invalid filter value 400
- **Detail** (GET /api/tasks/{id}/): found, not found 404, soft-deleted 404
- **Update** (PATCH /api/tasks/{id}/): partial update, title validation, soft-deleted 404, immutable fields ignored, status ignored, updated_at refreshed, tags deduped
- **Soft Delete** (DELETE /api/tasks/{id}/): sets deleted_at, returns 204, excluded from list, 404 on detail after, non-existent 404, already-deleted 404
- **Transition** (POST /api/tasks/{id}/transition/): all 4 valid transitions, 2 invalid transitions with error format, non-existent task 404, soft-deleted 404, missing direction 400, invalid direction 400
- **Error format** (Scenarios E-01/E-02/E-03): verify `{"error": {"code": ..., "message": ..., "details": ...}}` shape

**Spec refs**: All REQ-C-*, REQ-L-*, REQ-D-*, REQ-U-*, REQ-SD-*, REQ-T-*, REQ-F-*, REQ-E-*

**Design refs**: Design §1.3 sequence diagrams; Design §2.5/2.6/2.8

**Acceptance criteria**:
- Uses `APITestCase` and `APIClient` throughout
- Each test method maps to a named scenario from the spec
- Error format assertions check for `response.data["error"]["code"]`
- `python manage.py test tasks.tests.test_views` passes with all tests green
- Total test count for this file: at minimum 35 test methods

**Dependencies**: 3.5 (all API wiring complete)

**Files**:
- `tasks/tests/test_views.py` (create)

**Status**: pending

---

## Phase 5: Verification

### Task 5.1 — Run full test suite and verify all pass

**Description**: Execute the complete test suite with `python manage.py test tasks`. Fix any failures found. Do NOT modify spec or design — fix implementation to match spec. Document any discrepancies found.

**Spec refs**: All

**Design refs**: All

**Acceptance criteria**:
- `python manage.py test tasks` exits with 0 failures, 0 errors
- All 4 test modules run: test_models, test_serializers, test_services, test_views
- No `DeprecationWarning` that indicate forward-incompatibility issues

**Dependencies**: 4.1, 4.2, 4.3, 4.4

**Files**:
- Any implementation files that needed fixes during this phase

**Status**: pending

---

### Task 5.2 — Run migrations and manual smoke test via DRF browsable API

**Description**: Run `python manage.py migrate` on a fresh database. Start the development server with `python manage.py runserver`. Manually verify using the DRF browsable API at `http://localhost:8000/api/tasks/`: create a task, list tasks, retrieve one, update it, transition it forward, soft-delete it, verify it disappears from list.

**Spec refs**: REQ-C-001/009; REQ-L-001/004; REQ-D-001; REQ-U-001/007; REQ-T-001/007; REQ-SD-001/003/006

**Design refs**: Design §1.2 Layer Separation; §1.3 sequence diagrams

**Acceptance criteria**:
- `python manage.py migrate` completes with no errors on fresh DB
- `python manage.py runserver` starts with no import errors
- DRF browsable API accessible at `http://localhost:8000/api/tasks/`
- Manual CRUD flow completes successfully end-to-end
- Soft-deleted task does not appear in list endpoint after deletion

**Dependencies**: 5.1

**Files**:
- No code changes expected; this is a verification task

**Status**: pending

---

## Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| 1: Infrastructure | 1.1 – 1.4 | Project/app scaffolding, requirements, settings, root URLs |
| 2: Core Implementation | 2.1 – 2.5 | Managers, model, migration, serializers, services |
| 3: API Layer | 3.1 – 3.6 | Exception handler, filters, views, URLs, admin |
| 4: Testing | 4.1 – 4.4 | Model, serializer, service, and view tests |
| 5: Verification | 5.1 – 5.2 | Full test run and manual smoke test |
| **Total** | **22** | |

### Dependency Graph (abbreviated)

```
1.1 ──► 1.3 ──► 1.4 ──────────────────────────────────────► 3.5 ──► 4.4
1.2                                                                        │
1.1 ──► 2.1 ──► 2.2 ──► 2.3 ──► 4.1                                     │
                  │                                                         │
                  ├──── 2.4 ──────────────────── 4.2                      │
                  │                                │                        │
                  └──── 3.2 ──► 3.3 ──► 3.4 ──►─┘                       │
                                  │                                         │
2.5 ──────────────────────────────┤                                        │
                                  │                                         │
3.1 ──────────────────────────────┘                                        │
                                                                            ▼
                                                              5.1 ──► 5.2
```
