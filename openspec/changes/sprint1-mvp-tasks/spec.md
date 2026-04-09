# Spec — sprint1-mvp-tasks

**Change**: Sprint 1 MVP — Task Management Backend
**Status**: draft
**Date**: 2026-04-09
**Author**: SDD Spec Agent

---

## Overview

This document specifies the functional requirements and acceptance scenarios for Sprint 1 of AITasks. It covers the complete REST API for task management: creation, listing, detail, update, soft delete, state transitions, filtering, pagination, validation, and error formatting.

All requirements use RFC 2119 keywords: MUST, SHALL, SHOULD, MAY, MUST NOT, SHALL NOT.

---

## 1. Task Model

### Requirements

- **REQ-M-001**: The `Task` model MUST use a UUID as primary key, auto-generated on creation and never editable.
- **REQ-M-002**: `title` MUST be stored as varchar(200), MUST NOT be null, and MUST be at least 3 characters after trimming whitespace.
- **REQ-M-003**: `description` MUST be stored as text, MAY be empty string, and MUST default to `""`.
- **REQ-M-004**: `priority` MUST be one of `low`, `medium`, `high`. It MUST NOT be null. Default MUST be `medium`.
- **REQ-M-005**: `status` MUST be one of `TODO`, `IN_PROGRESS`, `DONE`. It MUST NOT be null. Default on creation MUST be `TODO`.
- **REQ-M-006**: `due_date` MUST be stored as a date (no time component). It MAY be null.
- **REQ-M-007**: `tags` MUST be stored as a JSON array of strings. It MUST default to an empty list `[]`. Duplicate entries MUST be removed before persistence.
- **REQ-M-008**: `created_at` MUST be set automatically on creation and MUST NOT be modifiable through the API.
- **REQ-M-009**: `updated_at` MUST be set automatically on every save.
- **REQ-M-010**: `deleted_at` MUST be null by default. When a task is soft-deleted, `deleted_at` MUST be set to the current UTC datetime. It MUST NOT be writable through the standard update endpoint.
- **REQ-M-011**: The default manager MUST return only tasks where `deleted_at IS NULL`. A secondary manager `all_objects` MUST provide access to all rows including soft-deleted ones.
- **REQ-M-012**: The model MUST have database indices on: `created_at`, `status`, `priority`, `deleted_at`, and the composite `(deleted_at, created_at)`.

### Scenarios

#### Scenario M-01: UUID primary key is auto-generated
```
Given a new Task is created with valid data
When the Task is saved to the database
Then the Task's id field MUST be a valid UUID v4
And the id MUST be unique
And the id MUST NOT be modifiable after creation
```

#### Scenario M-02: Default values on new Task
```
Given a Task is created with only a title
When the Task is retrieved from the database
Then priority MUST equal "medium"
And status MUST equal "TODO"
And description MUST equal ""
And tags MUST equal []
And deleted_at MUST be null
And created_at MUST be set to approximately now (UTC)
```

#### Scenario M-03: Alive manager excludes soft-deleted tasks
```
Given a soft-deleted Task exists (deleted_at is set)
When Task.objects.all() is called (default manager)
Then the soft-deleted Task MUST NOT appear in the queryset
```

#### Scenario M-04: all_objects manager includes soft-deleted tasks
```
Given a soft-deleted Task exists
When Task.all_objects.all() is called
Then the soft-deleted Task MUST appear in the queryset
```

#### Scenario M-05: Tags deduplication at model level
```
Given a Task is created with tags ["a", "b", "a"]
When the Task is saved
Then Task.tags MUST equal ["a", "b"] (order may vary, duplicates removed)
```

---

## 2. Task Creation — POST /api/tasks/

### Requirements

- **REQ-C-001**: The endpoint MUST accept `POST /api/tasks/` with a JSON body.
- **REQ-C-002**: `title` MUST be required in the request body. Omitting it MUST return `400 Bad Request`.
- **REQ-C-003**: `title` MUST be trimmed before validation and persistence. A title consisting only of whitespace MUST be rejected with `400`.
- **REQ-C-004**: `title` after trimming MUST be between 3 and 200 characters. Violations MUST return `400`.
- **REQ-C-005**: `status` MUST NOT be accepted in the create body. The status MUST always be initialized to `TODO`.
- **REQ-C-006**: `priority` in the request body MUST be one of `low`, `medium`, `high`. An invalid value MUST return `400`. If omitted, it MUST default to `medium`.
- **REQ-C-007**: `due_date` MUST be accepted as ISO 8601 date string (`YYYY-MM-DD`). An invalid date format MUST return `400`. Omitting it is valid.
- **REQ-C-008**: `tags` MUST be accepted as a JSON array of strings. Non-string elements MUST cause a `400`. Omitting it defaults to `[]`. Duplicate tags MUST be removed before saving.
- **REQ-C-009**: A successful creation MUST return `201 Created` with the full task representation in the response body.
- **REQ-C-010**: The response body MUST include: `id`, `title`, `description`, `priority`, `status`, `due_date`, `tags`, `created_at`, `updated_at`. It MUST NOT include `deleted_at`.

### Scenarios

#### Scenario C-01: Create task with only required field
```
Given a POST request to /api/tasks/ with body {"title": "Buy milk"}
When the request is processed
Then the response status MUST be 201
And the response body MUST contain the created task
And status MUST be "TODO"
And priority MUST be "medium"
And tags MUST be []
And description MUST be ""
And id MUST be a valid UUID
```

#### Scenario C-02: Create task with all fields
```
Given a POST request to /api/tasks/ with body:
  {"title": "Deploy to staging", "description": "Run smoke tests after", "priority": "high", "due_date": "2026-05-01", "tags": ["devops", "release"]}
When the request is processed
Then the response status MUST be 201
And each provided field MUST match the value in the response
And status MUST be "TODO" (not overridable at creation)
```

#### Scenario C-03: Reject missing title
```
Given a POST request to /api/tasks/ with body {"priority": "high"}
When the request is processed
Then the response status MUST be 400
And the error envelope MUST contain code "validation_error"
And the details MUST reference the "title" field
```

#### Scenario C-04: Reject title shorter than 3 chars after trim
```
Given a POST request to /api/tasks/ with body {"title": "ab"}
When the request is processed
Then the response status MUST be 400
And the error details MUST reference the "title" field
```

#### Scenario C-05: Reject whitespace-only title
```
Given a POST request to /api/tasks/ with body {"title": "   "}
When the request is processed
Then the response status MUST be 400
And the error details MUST reference the "title" field
```

#### Scenario C-06: Reject title exceeding 200 chars
```
Given a POST request to /api/tasks/ with body {"title": "<201-char string>"}
When the request is processed
Then the response status MUST be 400
And the error details MUST reference the "title" field
```

#### Scenario C-07: Reject invalid priority value
```
Given a POST request to /api/tasks/ with body {"title": "Test", "priority": "urgent"}
When the request is processed
Then the response status MUST be 400
And the error details MUST reference the "priority" field
```

#### Scenario C-08: Reject invalid due_date format
```
Given a POST request to /api/tasks/ with body {"title": "Test", "due_date": "15/04/2026"}
When the request is processed
Then the response status MUST be 400
And the error details MUST reference the "due_date" field
```

#### Scenario C-09: Reject non-string tag elements
```
Given a POST request to /api/tasks/ with body {"title": "Test", "tags": ["valid", 42]}
When the request is processed
Then the response status MUST be 400
And the error details MUST reference the "tags" field
```

#### Scenario C-10: Tags are deduplicated on creation
```
Given a POST request to /api/tasks/ with body {"title": "Test", "tags": ["work", "urgent", "work"]}
When the request is processed
Then the response status MUST be 201
And the tags in the response MUST contain only unique values: ["work", "urgent"] (order may vary)
```

#### Scenario C-11: Status field in request body is ignored
```
Given a POST request to /api/tasks/ with body {"title": "Test", "status": "DONE"}
When the request is processed
Then the response status MUST be 201
And the task status in the response MUST be "TODO"
```

---

## 3. Task Listing — GET /api/tasks/

### Requirements

- **REQ-L-001**: The endpoint MUST return only tasks where `deleted_at IS NULL`.
- **REQ-L-002**: Results MUST be ordered by `created_at DESC` (newest first).
- **REQ-L-003**: Pagination MUST be applied. Default page size is 20. `page_size` query param MAY override the default.
- **REQ-L-004**: The response MUST follow the shape: `{"count": int, "next": url|null, "previous": url|null, "results": [...]}`.
- **REQ-L-005**: Each task in `results` MUST include: `id`, `title`, `description`, `priority`, `status`, `due_date`, `tags`, `created_at`, `updated_at`. It MUST NOT include `deleted_at`.
- **REQ-L-006**: Filtering by `status` query param MUST be supported. Valid values: `TODO`, `IN_PROGRESS`, `DONE`.
- **REQ-L-007**: Filtering by `priority` query param MUST be supported. Valid values: `low`, `medium`, `high`.
- **REQ-L-008**: Status and priority filters MUST be combinable in the same request.
- **REQ-L-009**: An empty result set MUST return `200 OK` with `count: 0` and `results: []`, not a 404.
- **REQ-L-010**: Invalid filter values SHOULD return `400 Bad Request` with a descriptive error.

### Scenarios

#### Scenario L-01: List returns only non-deleted tasks
```
Given three tasks exist: two alive and one soft-deleted
When a GET request is made to /api/tasks/
Then the response status MUST be 200
And results MUST contain exactly 2 tasks
And the soft-deleted task MUST NOT appear
```

#### Scenario L-02: Results ordered newest first
```
Given task A was created at 10:00 and task B was created at 11:00
When a GET request is made to /api/tasks/
Then task B MUST appear before task A in the results
```

#### Scenario L-03: Pagination with default page size
```
Given 25 alive tasks exist
When a GET request is made to /api/tasks/
Then count MUST be 25
And results MUST contain exactly 20 tasks
And next MUST be a non-null URL pointing to page 2
And previous MUST be null
```

#### Scenario L-04: Pagination second page
```
Given 25 alive tasks exist
When a GET request is made to /api/tasks/?page=2
Then results MUST contain exactly 5 tasks
And previous MUST be a non-null URL
And next MUST be null
```

#### Scenario L-05: Empty list returns 200
```
Given no alive tasks exist
When a GET request is made to /api/tasks/
Then the response status MUST be 200
And count MUST be 0
And results MUST be []
```

#### Scenario L-06: Filter by status=TODO
```
Given tasks exist with statuses: [TODO, TODO, IN_PROGRESS, DONE]
When a GET request is made to /api/tasks/?status=TODO
Then results MUST contain exactly 2 tasks
And all returned tasks MUST have status "TODO"
```

#### Scenario L-07: Filter by priority=high
```
Given tasks exist with priorities: [high, high, medium, low]
When a GET request is made to /api/tasks/?priority=high
Then results MUST contain exactly 2 tasks
And all returned tasks MUST have priority "high"
```

#### Scenario L-08: Combined filter status + priority
```
Given tasks exist: [TODO+high, TODO+medium, IN_PROGRESS+high, DONE+high]
When a GET request is made to /api/tasks/?status=TODO&priority=high
Then results MUST contain exactly 1 task
And that task MUST have status "TODO" AND priority "high"
```

#### Scenario L-09: Custom page_size
```
Given 10 alive tasks exist
When a GET request is made to /api/tasks/?page_size=5
Then results MUST contain exactly 5 tasks
And count MUST be 10
And next MUST be non-null
```

---

## 4. Task Detail — GET /api/tasks/{id}/

### Requirements

- **REQ-D-001**: The endpoint MUST return the full task representation for a valid, non-deleted task.
- **REQ-D-002**: If the task does not exist (UUID not found), the response MUST be `404 Not Found`.
- **REQ-D-003**: If the task exists but `deleted_at` is set, the response MUST be `404 Not Found` (same behavior as non-existent).
- **REQ-D-004**: The response body for a found task MUST include: `id`, `title`, `description`, `priority`, `status`, `due_date`, `tags`, `created_at`, `updated_at`. It MUST NOT include `deleted_at`.

### Scenarios

#### Scenario D-01: Retrieve existing alive task
```
Given a task with id "abc-123" exists and is not soft-deleted
When a GET request is made to /api/tasks/abc-123/
Then the response status MUST be 200
And the response body MUST contain all task fields
And deleted_at MUST NOT be present in the response
```

#### Scenario D-02: Task not found returns 404
```
Given no task with id "nonexistent-uuid" exists
When a GET request is made to /api/tasks/nonexistent-uuid/
Then the response status MUST be 404
And the error envelope MUST be present
```

#### Scenario D-03: Soft-deleted task returns 404
```
Given a task with id "abc-123" exists and has deleted_at set
When a GET request is made to /api/tasks/abc-123/
Then the response status MUST be 404
(behavior is identical to a non-existent task)
```

---

## 5. Task Update — PATCH /api/tasks/{id}/

### Requirements

- **REQ-U-001**: The endpoint MUST support partial update (PATCH semantics). Only fields included in the request body MUST be updated.
- **REQ-U-002**: `title`, `description`, `priority`, `due_date`, and `tags` MUST be updatable.
- **REQ-U-003**: `id`, `created_at`, and `deleted_at` MUST NOT be modifiable through this endpoint. If present in the body, they MUST be ignored or cause a `400`.
- **REQ-U-004**: `status` MUST NOT be updatable through PATCH. Status changes MUST go through the transition endpoint.
- **REQ-U-005**: Updating a soft-deleted task MUST return `404 Not Found`.
- **REQ-U-006**: The same validation rules as creation apply: title length (3–200), priority enum, due_date format, tags as list of strings with dedup.
- **REQ-U-007**: A successful update MUST return `200 OK` with the full updated task representation.
- **REQ-U-008**: `updated_at` MUST be refreshed automatically on every successful update.

### Scenarios

#### Scenario U-01: Partial update changes only sent fields
```
Given a task exists with title "Old title", priority "low", status "TODO"
When a PATCH request is made to /api/tasks/{id}/ with body {"priority": "high"}
Then the response status MUST be 200
And the priority in the response MUST be "high"
And the title MUST still be "Old title"
And the status MUST still be "TODO"
```

#### Scenario U-02: Update title with validation
```
Given a task exists
When a PATCH request is made with body {"title": "ab"}
Then the response status MUST be 400
And the error details MUST reference the "title" field
```

#### Scenario U-03: Reject update on soft-deleted task
```
Given a task exists and is soft-deleted
When a PATCH request is made to /api/tasks/{id}/ with body {"title": "New title"}
Then the response status MUST be 404
```

#### Scenario U-04: Immutable fields are not updated
```
Given a task exists with id "abc-123"
When a PATCH request is made with body {"id": "new-uuid", "created_at": "2020-01-01T00:00:00Z"}
Then the response status MUST be 200 (fields silently ignored) OR 400
And the task id MUST still be "abc-123"
And the created_at MUST NOT change
```

#### Scenario U-05: Status cannot be changed via PATCH
```
Given a task exists with status "TODO"
When a PATCH request is made with body {"status": "DONE"}
Then the task status MUST remain "TODO" (field ignored)
OR the response MUST be 400 with an error referencing "status"
```

#### Scenario U-06: updated_at is refreshed on successful update
```
Given a task exists with a known updated_at timestamp
When a PATCH request is made with a valid body
Then the updated_at in the response MUST be greater than or equal to the original updated_at
```

#### Scenario U-07: Update tags with deduplication
```
Given a task exists
When a PATCH request is made with body {"tags": ["x", "y", "x"]}
Then the response status MUST be 200
And the tags in the response MUST be ["x", "y"] (duplicates removed)
```

---

## 6. Task Soft Delete — DELETE /api/tasks/{id}/

### Requirements

- **REQ-SD-001**: The endpoint MUST NOT physically delete the database row.
- **REQ-SD-002**: On a successful delete, `deleted_at` MUST be set to the current UTC datetime.
- **REQ-SD-003**: A successful delete MUST return `204 No Content` with an empty body.
- **REQ-SD-004**: If the task does not exist, the response MUST be `404 Not Found`.
- **REQ-SD-005**: If the task is already soft-deleted, the endpoint MUST return `404 Not Found` (consistent with the rule that soft-deleted tasks are treated as non-existent).
- **REQ-SD-006**: After a soft delete, the task MUST NOT appear in list or detail endpoints.

### Scenarios

#### Scenario SD-01: Soft delete sets deleted_at
```
Given a task with id "abc-123" exists and is not deleted
When a DELETE request is made to /api/tasks/abc-123/
Then the response status MUST be 204
And the response body MUST be empty
And in the database, deleted_at MUST be set to a non-null datetime
And the row MUST still exist in the database
```

#### Scenario SD-02: Soft-deleted task is excluded from list
```
Given a task is soft-deleted
When a GET request is made to /api/tasks/
Then the soft-deleted task MUST NOT appear in results
```

#### Scenario SD-03: Soft-deleted task returns 404 on detail
```
Given a task is soft-deleted
When a GET request is made to /api/tasks/{id}/
Then the response status MUST be 404
```

#### Scenario SD-04: Delete non-existent task returns 404
```
Given no task with id "ghost-uuid" exists
When a DELETE request is made to /api/tasks/ghost-uuid/
Then the response status MUST be 404
```

#### Scenario SD-05: Already soft-deleted task returns 404 on repeat delete
```
Given a task has already been soft-deleted
When a DELETE request is made to /api/tasks/{id}/ again
Then the response status MUST be 404
```

---

## 7. State Transitions — POST /api/tasks/{id}/transition/

### Requirements

- **REQ-T-001**: The endpoint MUST accept `POST /api/tasks/{id}/transition/` with a JSON body containing `direction`.
- **REQ-T-002**: `direction` MUST be required. Valid values are `"forward"` and `"backward"`. Any other value MUST return `400`.
- **REQ-T-003**: Omitting `direction` MUST return `400`.
- **REQ-T-004**: The state transition matrix MUST be enforced:
  - `TODO` + `forward` → `IN_PROGRESS`
  - `IN_PROGRESS` + `forward` → `DONE`
  - `IN_PROGRESS` + `backward` → `TODO`
  - `DONE` + `backward` → `IN_PROGRESS`
- **REQ-T-005**: Invalid transitions MUST return `400 Bad Request`:
  - `TODO` + `backward` (no previous state)
  - `DONE` + `forward` (no next state)
- **REQ-T-006**: Attempting a transition on a soft-deleted task MUST return `404 Not Found`.
- **REQ-T-007**: A successful transition MUST return `200 OK` with the full updated task representation showing the new status.
- **REQ-T-008**: The transition logic MUST live in `tasks/services.py` as an isolated pure function, not in the view.
- **REQ-T-009**: `updated_at` MUST be refreshed on a successful transition.

### Scenarios

#### Scenario T-01: Forward transition TODO → IN_PROGRESS
```
Given a task with status "TODO"
When a POST request is made to /api/tasks/{id}/transition/ with body {"direction": "forward"}
Then the response status MUST be 200
And the task status in the response MUST be "IN_PROGRESS"
```

#### Scenario T-02: Forward transition IN_PROGRESS → DONE
```
Given a task with status "IN_PROGRESS"
When a POST request is made to /api/tasks/{id}/transition/ with body {"direction": "forward"}
Then the response status MUST be 200
And the task status in the response MUST be "DONE"
```

#### Scenario T-03: Backward transition IN_PROGRESS → TODO
```
Given a task with status "IN_PROGRESS"
When a POST request is made to /api/tasks/{id}/transition/ with body {"direction": "backward"}
Then the response status MUST be 200
And the task status in the response MUST be "TODO"
```

#### Scenario T-04: Backward transition DONE → IN_PROGRESS
```
Given a task with status "DONE"
When a POST request is made to /api/tasks/{id}/transition/ with body {"direction": "backward"}
Then the response status MUST be 200
And the task status in the response MUST be "IN_PROGRESS"
```

#### Scenario T-05: Invalid forward transition from DONE
```
Given a task with status "DONE"
When a POST request is made to /api/tasks/{id}/transition/ with body {"direction": "forward"}
Then the response status MUST be 400
And the error envelope MUST be present with a message describing the invalid transition
```

#### Scenario T-06: Invalid backward transition from TODO
```
Given a task with status "TODO"
When a POST request is made to /api/tasks/{id}/transition/ with body {"direction": "backward"}
Then the response status MUST be 400
And the error envelope MUST be present with a message describing the invalid transition
```

#### Scenario T-07: Transition on non-existent task returns 404
```
Given no task with id "ghost-uuid" exists
When a POST request is made to /api/tasks/ghost-uuid/transition/ with body {"direction": "forward"}
Then the response status MUST be 404
```

#### Scenario T-08: Transition on soft-deleted task returns 404
```
Given a task is soft-deleted
When a POST request is made to /api/tasks/{id}/transition/ with body {"direction": "forward"}
Then the response status MUST be 404
```

#### Scenario T-09: Missing direction field returns 400
```
Given a task with status "TODO"
When a POST request is made to /api/tasks/{id}/transition/ with body {}
Then the response status MUST be 400
And the error details MUST reference the "direction" field
```

#### Scenario T-10: Invalid direction value returns 400
```
Given a task with status "TODO"
When a POST request is made to /api/tasks/{id}/transition/ with body {"direction": "sideways"}
Then the response status MUST be 400
And the error details MUST reference the "direction" field
```

#### Scenario T-11: Skip transition TODO → DONE is not allowed
```
Given a task with status "TODO"
When a POST request is made to /api/tasks/{id}/transition/ with body {"direction": "forward"}
  (to move to IN_PROGRESS, then attempt to skip directly by other means)
Then no single API call SHALL move a task from "TODO" to "DONE" directly
(The API only supports one-step transitions — this is enforced by the matrix)
```

---

## 8. Filtering

### Requirements

- **REQ-F-001**: Filtering MUST be implemented using `django-filter` with a `FilterSet` class in `tasks/filters.py`.
- **REQ-F-002**: The `status` filter MUST only accept valid enum values: `TODO`, `IN_PROGRESS`, `DONE`. Invalid values MUST return `400`.
- **REQ-F-003**: The `priority` filter MUST only accept valid enum values: `low`, `medium`, `high`. Invalid values MUST return `400`.
- **REQ-F-004**: Both filters MUST be applicable simultaneously (AND semantics).
- **REQ-F-005**: Filters MUST apply after the default manager's soft-delete exclusion. A soft-deleted task matching the filter criteria MUST NOT appear.

### Scenarios

#### Scenario F-01: Filter by single status value
```
Given 5 tasks: 3 TODO, 2 IN_PROGRESS, all alive
When a GET request is made to /api/tasks/?status=IN_PROGRESS
Then count MUST be 2
And all results MUST have status "IN_PROGRESS"
```

#### Scenario F-02: Filter by single priority value
```
Given 4 tasks: 1 low, 2 medium, 1 high, all alive
When a GET request is made to /api/tasks/?priority=medium
Then count MUST be 2
And all results MUST have priority "medium"
```

#### Scenario F-03: Combined filter returns intersection
```
Given tasks:
  - Task A: status=TODO, priority=high
  - Task B: status=TODO, priority=low
  - Task C: status=IN_PROGRESS, priority=high
When a GET request is made to /api/tasks/?status=TODO&priority=high
Then count MUST be 1
And the result MUST be Task A only
```

#### Scenario F-04: Filter excludes soft-deleted tasks
```
Given Task A: status=TODO, alive; Task B: status=TODO, soft-deleted
When a GET request is made to /api/tasks/?status=TODO
Then count MUST be 1
And Task B MUST NOT appear
```

#### Scenario F-05: Invalid status filter value returns 400
```
Given a GET request is made to /api/tasks/?status=FINISHED
Then the response status MUST be 400
```

#### Scenario F-06: Invalid priority filter value returns 400
```
Given a GET request is made to /api/tasks/?priority=critical
Then the response status MUST be 400
```

#### Scenario F-07: Filter with no matching results returns empty list
```
Given all alive tasks have status "TODO"
When a GET request is made to /api/tasks/?status=DONE
Then the response status MUST be 200
And count MUST be 0
And results MUST be []
```

---

## 9. Error Format

### Requirements

- **REQ-E-001**: ALL error responses MUST use a consistent JSON envelope:
  ```json
  {
    "error": {
      "code": "<string>",
      "message": "<human-readable string>",
      "details": { "<field>": ["<error message>"] }
    }
  }
  ```
- **REQ-E-002**: `code` MUST be a machine-readable string. Recommended values:
  - `"validation_error"` for field validation failures (400)
  - `"not_found"` for missing or soft-deleted resources (404)
  - `"invalid_transition"` for state machine violations (400)
- **REQ-E-003**: `message` MUST be a human-readable description of the error.
- **REQ-E-004**: `details` MAY be omitted when there are no per-field specifics (e.g., 404 errors).
- **REQ-E-005**: A custom DRF exception handler MUST be registered in settings to produce this format for all error cases, including DRF's built-in exceptions.
- **REQ-E-006**: The error handler MUST NOT add business logic — its only responsibility is reshaping the error structure.

### Scenarios

#### Scenario E-01: Validation error includes field details
```
Given a POST request to /api/tasks/ with body {"title": "ab"}
When the request is processed
Then the response body MUST match:
  {
    "error": {
      "code": "validation_error",
      "message": "<descriptive message>",
      "details": {
        "title": ["<error about min length>"]
      }
    }
  }
```

#### Scenario E-02: Not found error uses consistent format
```
Given a GET request to /api/tasks/nonexistent-uuid/
When the request is processed
Then the response body MUST match:
  {
    "error": {
      "code": "not_found",
      "message": "<descriptive message>"
    }
  }
```

#### Scenario E-03: Invalid transition error uses consistent format
```
Given a task with status "DONE" and a forward transition request
When the request is processed
Then the response body MUST match:
  {
    "error": {
      "code": "invalid_transition",
      "message": "<message explaining DONE has no forward state>"
    }
  }
```

---

## 10. Validation Rules (Consolidated)

### Requirements

- **REQ-V-001 — title**: MUST be a non-empty string after trimming. Length MUST be 3–200 characters. Applied on create and update.
- **REQ-V-002 — priority**: MUST be one of `["low", "medium", "high"]`. Case-sensitive. Applied on create and update.
- **REQ-V-003 — status**: Not writable via create or PATCH. Only writable through the transition endpoint. If the serializer exposes it for creation, it MUST be ignored.
- **REQ-V-004 — due_date**: MUST be a valid date in ISO 8601 format (`YYYY-MM-DD`). Accepts `null`. Invalid strings MUST be rejected with `400`.
- **REQ-V-005 — tags**: MUST be a JSON array. Every element MUST be a string. Non-string elements MUST be rejected with `400`. Duplicates MUST be removed. Empty array `[]` is valid.
- **REQ-V-006 — direction** (transition): MUST be one of `["forward", "backward"]`. Required, non-nullable. Missing or invalid value MUST return `400`.
- **REQ-V-007 — Trim before validate**: `title` MUST be stripped of leading/trailing whitespace before length validation and persistence.
- **REQ-V-008 — Validation location**: Field validation for the Task MUST live in the DRF serializer's `validate_<field>` methods. State transition validation MUST live in `tasks/services.py`.

### Scenarios

#### Scenario V-01: Title at minimum boundary (3 chars)
```
Given a POST request with body {"title": "abc"}
When the request is processed
Then the response status MUST be 201
```

#### Scenario V-02: Title at maximum boundary (200 chars)
```
Given a POST request with body {"title": "<200-char string>"}
When the request is processed
Then the response status MUST be 201
```

#### Scenario V-03: Title one character over maximum (201 chars)
```
Given a POST request with body {"title": "<201-char string>"}
When the request is processed
Then the response status MUST be 400
```

#### Scenario V-04: Title trim reduces below minimum
```
Given a POST request with body {"title": "  a  "}
When the request is processed
Then the response status MUST be 400
(trimmed title is "a" — only 1 character, below the 3-char minimum)
```

#### Scenario V-05: due_date as null is valid
```
Given a POST request with body {"title": "Test", "due_date": null}
When the request is processed
Then the response status MUST be 201
And due_date in the response MUST be null
```

#### Scenario V-06: tags as empty array is valid
```
Given a POST request with body {"title": "Test", "tags": []}
When the request is processed
Then the response status MUST be 201
And tags in the response MUST be []
```

#### Scenario V-07: tags with non-string element is rejected
```
Given a POST request with body {"title": "Test", "tags": [true, "valid"]}
When the request is processed
Then the response status MUST be 400
And the error details MUST reference the "tags" field
```

#### Scenario V-08: tags as non-array is rejected
```
Given a POST request with body {"title": "Test", "tags": "single-tag"}
When the request is processed
Then the response status MUST be 400
And the error details MUST reference the "tags" field
```

---

## Appendix: State Transition Matrix

| Current Status | direction=forward | direction=backward |
|----------------|-------------------|-------------------|
| `TODO`         | `IN_PROGRESS`     | INVALID (400)     |
| `IN_PROGRESS`  | `DONE`            | `TODO`            |
| `DONE`         | INVALID (400)     | `IN_PROGRESS`     |

## Appendix: Field Summary

| Field        | Type            | Required (create) | Mutable (PATCH) | Default    |
|--------------|-----------------|-------------------|-----------------|------------|
| `id`         | UUID            | No (auto)         | No              | auto       |
| `title`      | string(3-200)   | Yes               | Yes             | —          |
| `description`| text            | No                | Yes             | `""`       |
| `priority`   | enum            | No                | Yes             | `"medium"` |
| `status`     | enum            | No (always TODO)  | Via /transition/| `"TODO"`   |
| `due_date`   | date / null     | No                | Yes             | `null`     |
| `tags`       | string[]        | No                | Yes             | `[]`       |
| `created_at` | datetime        | No (auto)         | No              | auto       |
| `updated_at` | datetime        | No (auto)         | No (auto)       | auto       |
| `deleted_at` | datetime / null | No                | No              | `null`     |
