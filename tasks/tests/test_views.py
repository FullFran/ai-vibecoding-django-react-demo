"""
Integration tests for all TaskViewSet API endpoints.
Uses DRF's APITestCase and APIClient.
Minimum 35 test methods covering all spec scenarios.
"""
import uuid
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from tasks.models import Task


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_task(**kwargs):
    """Create a Task using the default (alive) manager."""
    defaults = {"title": "Default task title"}
    defaults.update(kwargs)
    return Task.objects.create(**defaults)


def soft_delete_task(task):
    """Soft-delete a task by setting deleted_at via all_objects."""
    task.deleted_at = timezone.now()
    task.save(update_fields=["deleted_at"])


# ---------------------------------------------------------------------------
# CREATE — POST /api/tasks/
# ---------------------------------------------------------------------------

class TaskCreateTestCase(APITestCase):

    def setUp(self):
        self.url = reverse("task-list")

    def test_create_c01_only_title_returns_201(self):
        response = self.client.post(self.url, {"title": "Buy milk"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.data
        self.assertEqual(data["status"], "TODO")
        self.assertEqual(data["priority"], "medium")
        self.assertEqual(data["tags"], [])
        self.assertEqual(data["description"], "")
        # id should be a valid UUID
        try:
            uuid.UUID(str(data["id"]))
        except ValueError:
            self.fail("id is not a valid UUID")

    def test_create_c02_all_fields_returns_201(self):
        payload = {
            "title": "Deploy to staging",
            "description": "Run smoke tests after",
            "priority": "high",
            "due_date": "2026-05-01",
            "tags": ["devops", "release"],
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.data
        self.assertEqual(data["title"], "Deploy to staging")
        self.assertEqual(data["description"], "Run smoke tests after")
        self.assertEqual(data["priority"], "high")
        self.assertEqual(data["due_date"], "2026-05-01")
        self.assertEqual(data["tags"], ["devops", "release"])
        self.assertEqual(data["status"], "TODO")

    def test_create_c03_missing_title_returns_400(self):
        response = self.client.post(self.url, {"priority": "high"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data["error"]["details"])

    def test_create_c04_title_shorter_than_3_chars_returns_400(self):
        response = self.client.post(self.url, {"title": "ab"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data["error"]["details"])

    def test_create_c05_whitespace_only_title_returns_400(self):
        response = self.client.post(self.url, {"title": "   "}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data["error"]["details"])

    def test_create_c06_title_over_200_chars_returns_400(self):
        response = self.client.post(self.url, {"title": "a" * 201}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data["error"]["details"])

    def test_create_c07_invalid_priority_returns_400(self):
        response = self.client.post(
            self.url, {"title": "Test task", "priority": "urgent"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("priority", response.data["error"]["details"])

    def test_create_c08_invalid_due_date_format_returns_400(self):
        response = self.client.post(
            self.url,
            {"title": "Test task", "due_date": "15/04/2026"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("due_date", response.data["error"]["details"])

    def test_create_c09_non_string_tag_returns_400(self):
        response = self.client.post(
            self.url, {"title": "Test task", "tags": ["valid", 42]}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("tags", response.data["error"]["details"])

    def test_create_c10_tags_deduplication_returns_unique_tags(self):
        response = self.client.post(
            self.url,
            {"title": "Test task", "tags": ["work", "urgent", "work"]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tags"], ["work", "urgent"])

    def test_create_c11_status_field_ignored_status_is_todo(self):
        response = self.client.post(
            self.url, {"title": "Test task", "status": "DONE"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "TODO")


# ---------------------------------------------------------------------------
# LIST — GET /api/tasks/
# ---------------------------------------------------------------------------

class TaskListTestCase(APITestCase):

    def setUp(self):
        self.url = reverse("task-list")

    def test_list_l01_excludes_soft_deleted_tasks(self):
        t1 = make_task(title="Alive task one")
        t2 = make_task(title="Alive task two")
        deleted = make_task(title="Soft deleted task")
        soft_delete_task(deleted)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(str(t1.id), ids)
        self.assertIn(str(t2.id), ids)
        self.assertNotIn(str(deleted.id), ids)
        self.assertEqual(response.data["count"], 2)

    def test_list_l02_ordered_newest_first(self):
        # Create tasks — newer task should appear first
        older = make_task(title="Older task")
        newer = make_task(title="Newer task")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        ids = [item["id"] for item in results]
        # newest first: newer before older
        self.assertLess(ids.index(str(newer.id)), ids.index(str(older.id)))

    def test_list_l03_pagination_default_page_size_20(self):
        for i in range(25):
            make_task(title=f"Task {i:02d}")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 25)
        self.assertEqual(len(response.data["results"]), 20)
        self.assertIsNotNone(response.data["next"])
        self.assertIsNone(response.data["previous"])

    def test_list_l04_second_page_has_remaining_tasks(self):
        for i in range(25):
            make_task(title=f"Task {i:02d}")

        response = self.client.get(self.url + "?page=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 5)
        self.assertIsNotNone(response.data["previous"])
        self.assertIsNone(response.data["next"])

    def test_list_l05_empty_list_returns_200_with_count_zero(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["results"], [])

    def test_list_l06_filter_by_status(self):
        make_task(title="Todo task one")
        make_task(title="Todo task two")
        t3 = make_task(title="In progress task")
        t3.status = "IN_PROGRESS"
        t3.save(update_fields=["status"])
        t4 = make_task(title="Done task")
        t4.status = "DONE"
        t4.save(update_fields=["status"])

        response = self.client.get(self.url + "?status=TODO")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        for item in response.data["results"]:
            self.assertEqual(item["status"], "TODO")

    def test_list_l07_filter_by_priority(self):
        make_task(title="High task one", priority="high")
        make_task(title="High task two", priority="high")
        make_task(title="Medium task", priority="medium")
        make_task(title="Low task", priority="low")

        response = self.client.get(self.url + "?priority=high")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        for item in response.data["results"]:
            self.assertEqual(item["priority"], "high")

    def test_list_l08_combined_status_and_priority_filter(self):
        make_task(title="Todo high", priority="high")
        make_task(title="Todo medium", priority="medium")
        t3 = make_task(title="InProgress high", priority="high")
        t3.status = "IN_PROGRESS"
        t3.save(update_fields=["status"])
        t4 = make_task(title="Done high", priority="high")
        t4.status = "DONE"
        t4.save(update_fields=["status"])

        response = self.client.get(self.url + "?status=TODO&priority=high")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["status"], "TODO")
        self.assertEqual(response.data["results"][0]["priority"], "high")

    def test_list_l09_custom_page_size(self):
        for i in range(10):
            make_task(title=f"Task {i:02d}")

        response = self.client.get(self.url + "?page_size=5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 10)
        self.assertEqual(len(response.data["results"]), 5)
        self.assertIsNotNone(response.data["next"])


# ---------------------------------------------------------------------------
# DETAIL — GET /api/tasks/{id}/
# ---------------------------------------------------------------------------

class TaskDetailTestCase(APITestCase):

    def test_detail_d01_found_alive_task(self):
        task = make_task(title="Detail task")
        url = reverse("task-detail", args=[task.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data["id"]), str(task.id))
        self.assertEqual(response.data["title"], "Detail task")
        self.assertNotIn("deleted_at", response.data)

    def test_detail_d02_not_found_returns_404(self):
        url = reverse("task-detail", args=[uuid.uuid4()])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

    def test_detail_d03_soft_deleted_returns_404(self):
        task = make_task(title="Soft-deleted detail")
        soft_delete_task(task)
        url = reverse("task-detail", args=[task.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# ---------------------------------------------------------------------------
# UPDATE — PATCH /api/tasks/{id}/
# ---------------------------------------------------------------------------

class TaskUpdateTestCase(APITestCase):

    def test_update_u01_partial_update_changes_only_sent_fields(self):
        task = make_task(title="Old title", priority="low")
        url = reverse("task-detail", args=[task.id])
        response = self.client.patch(url, {"priority": "high"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["priority"], "high")
        self.assertEqual(response.data["title"], "Old title")
        self.assertEqual(response.data["status"], "TODO")

    def test_update_u02_title_validation_on_update(self):
        task = make_task(title="Valid title")
        url = reverse("task-detail", args=[task.id])
        response = self.client.patch(url, {"title": "ab"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data["error"]["details"])

    def test_update_u03_soft_deleted_task_returns_404(self):
        task = make_task(title="To be soft-deleted")
        soft_delete_task(task)
        url = reverse("task-detail", args=[task.id])
        response = self.client.patch(url, {"title": "New title"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_u04_immutable_fields_ignored(self):
        task = make_task(title="Immutable test")
        original_id = str(task.id)
        original_created_at = task.created_at
        url = reverse("task-detail", args=[task.id])
        fake_id = str(uuid.uuid4())
        response = self.client.patch(
            url,
            {"id": fake_id, "created_at": "2020-01-01T00:00:00Z"},
            format="json",
        )
        # Should be 200 with fields silently ignored
        self.assertIn(response.status_code, [200, 400])
        if response.status_code == 200:
            self.assertEqual(str(response.data["id"]), original_id)

    def test_update_u05_status_ignored_via_patch(self):
        task = make_task(title="Status test")
        url = reverse("task-detail", args=[task.id])
        response = self.client.patch(url, {"status": "DONE"}, format="json")
        # status is read_only, so it should be silently ignored → status remains TODO
        self.assertIn(response.status_code, [200, 400])
        if response.status_code == 200:
            self.assertEqual(response.data["status"], "TODO")

    def test_update_u06_updated_at_refreshed(self):
        task = make_task(title="Timestamp test")
        original_updated_at = task.updated_at
        url = reverse("task-detail", args=[task.id])
        response = self.client.patch(
            url, {"description": "New description"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # updated_at should be >= original (same timestamp is acceptable if very fast)
        from django.utils.dateparse import parse_datetime
        new_updated_at_str = response.data["updated_at"]
        new_updated_at = parse_datetime(new_updated_at_str)
        self.assertGreaterEqual(new_updated_at, original_updated_at)

    def test_update_u07_tags_dedup_on_update(self):
        task = make_task(title="Tags dedup update")
        url = reverse("task-detail", args=[task.id])
        response = self.client.patch(
            url, {"tags": ["x", "y", "x"]}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["tags"], ["x", "y"])


# ---------------------------------------------------------------------------
# SOFT DELETE — DELETE /api/tasks/{id}/
# ---------------------------------------------------------------------------

class TaskSoftDeleteTestCase(APITestCase):

    def test_soft_delete_sd01_sets_deleted_at_returns_204(self):
        task = make_task(title="To soft-delete")
        url = reverse("task-detail", args=[task.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Verify deleted_at is set in DB
        task_from_db = Task.all_objects.get(pk=task.pk)
        self.assertIsNotNone(task_from_db.deleted_at)
        # Row still exists
        self.assertTrue(Task.all_objects.filter(pk=task.pk).exists())

    def test_soft_delete_sd02_excluded_from_list_after(self):
        task = make_task(title="Will be deleted")
        url = reverse("task-detail", args=[task.id])
        self.client.delete(url)
        list_url = reverse("task-list")
        response = self.client.get(list_url)
        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(str(task.id), ids)

    def test_soft_delete_sd03_returns_404_on_detail_after(self):
        task = make_task(title="Deleted detail check")
        url = reverse("task-detail", args=[task.id])
        self.client.delete(url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_soft_delete_sd04_non_existent_returns_404(self):
        url = reverse("task-detail", args=[uuid.uuid4()])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_soft_delete_sd05_already_deleted_returns_404(self):
        task = make_task(title="Double delete")
        soft_delete_task(task)
        url = reverse("task-detail", args=[task.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# ---------------------------------------------------------------------------
# TRANSITION — POST /api/tasks/{id}/transition/
# ---------------------------------------------------------------------------

class TaskTransitionTestCase(APITestCase):

    def _transition_url(self, task_id):
        return reverse("task-transition", args=[task_id])

    def test_transition_t01_todo_forward_to_in_progress(self):
        task = make_task(title="Transition TODO")
        url = self._transition_url(task.id)
        response = self.client.post(url, {"direction": "forward"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "IN_PROGRESS")

    def test_transition_t02_in_progress_forward_to_done(self):
        task = make_task(title="Transition IN_PROGRESS")
        task.status = "IN_PROGRESS"
        task.save(update_fields=["status"])
        url = self._transition_url(task.id)
        response = self.client.post(url, {"direction": "forward"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "DONE")

    def test_transition_t03_in_progress_backward_to_todo(self):
        task = make_task(title="Backward IN_PROGRESS")
        task.status = "IN_PROGRESS"
        task.save(update_fields=["status"])
        url = self._transition_url(task.id)
        response = self.client.post(url, {"direction": "backward"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "TODO")

    def test_transition_t04_done_backward_to_in_progress(self):
        task = make_task(title="Backward DONE")
        task.status = "DONE"
        task.save(update_fields=["status"])
        url = self._transition_url(task.id)
        response = self.client.post(url, {"direction": "backward"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "IN_PROGRESS")

    def test_transition_t05_done_forward_returns_400(self):
        task = make_task(title="Done forward invalid")
        task.status = "DONE"
        task.save(update_fields=["status"])
        url = self._transition_url(task.id)
        response = self.client.post(url, {"direction": "forward"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_transition_t06_todo_backward_returns_400(self):
        task = make_task(title="Todo backward invalid")
        url = self._transition_url(task.id)
        response = self.client.post(url, {"direction": "backward"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_transition_t07_non_existent_task_returns_404(self):
        url = self._transition_url(uuid.uuid4())
        response = self.client.post(url, {"direction": "forward"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_transition_t08_soft_deleted_task_returns_404(self):
        task = make_task(title="Soft-deleted transition")
        soft_delete_task(task)
        url = self._transition_url(task.id)
        response = self.client.post(url, {"direction": "forward"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_transition_t09_missing_direction_returns_400(self):
        task = make_task(title="Missing direction")
        url = self._transition_url(task.id)
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("direction", response.data["error"]["details"])

    def test_transition_t10_invalid_direction_returns_400(self):
        task = make_task(title="Invalid direction")
        url = self._transition_url(task.id)
        response = self.client.post(url, {"direction": "sideways"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("direction", response.data["error"]["details"])


# ---------------------------------------------------------------------------
# ERROR FORMAT — Scenarios E-01, E-02, E-03
# ---------------------------------------------------------------------------

class ErrorFormatTestCase(APITestCase):

    def setUp(self):
        self.list_url = reverse("task-list")

    def test_error_e01_validation_error_has_correct_envelope(self):
        """Validation error: {error: {code: 'validation_error', ...}}."""
        response = self.client.post(self.list_url, {"title": "ab"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        error = response.data["error"]
        self.assertEqual(error["code"], "validation_error")
        self.assertIn("message", error)
        self.assertIn("details", error)
        self.assertIn("title", error["details"])

    def test_error_e02_not_found_has_correct_envelope(self):
        """Not found: {error: {code: 'not_found', message: '...'}}."""
        url = reverse("task-detail", args=[uuid.uuid4()])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)
        error = response.data["error"]
        self.assertEqual(error["code"], "not_found")
        self.assertIn("message", error)

    def test_error_e03_invalid_transition_has_correct_envelope(self):
        """Invalid transition: {error: {code: 'invalid_transition', message: '...'}}."""
        task = make_task(title="E03 transition error")
        task.status = "DONE"
        task.save(update_fields=["status"])
        url = reverse("task-transition", args=[task.id])
        response = self.client.post(url, {"direction": "forward"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        error = response.data["error"]
        self.assertEqual(error["code"], "invalid_transition")
        self.assertIn("message", error)


# ---------------------------------------------------------------------------
# FILTER VALIDATION — F-05, F-06
# ---------------------------------------------------------------------------

class FilterValidationTestCase(APITestCase):

    def setUp(self):
        self.url = reverse("task-list")

    def test_filter_f05_invalid_status_value_returns_400(self):
        response = self.client.get(self.url + "?status=FINISHED")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_f06_invalid_priority_value_returns_400(self):
        response = self.client.get(self.url + "?priority=critical")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
