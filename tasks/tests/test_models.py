"""
Unit tests for the Task model.
Covers scenarios M-01 through M-05.
"""
import uuid
from django.test import TestCase
from django.utils import timezone

from tasks.models import Task


class TaskModelUUIDTestCase(TestCase):
    """M-01: UUID primary key is auto-generated."""

    def test_m01_uuid_is_auto_generated(self):
        """Task id should be a UUID after creation."""
        task = Task.objects.create(title="Test task")
        self.assertIsInstance(task.id, uuid.UUID)

    def test_m01_uuid_is_unique(self):
        """Two tasks must have different ids."""
        task1 = Task.objects.create(title="Task one")
        task2 = Task.objects.create(title="Task two")
        self.assertNotEqual(task1.id, task2.id)

    def test_m01_uuid_not_empty(self):
        """Task id must not be None or empty."""
        task = Task.objects.create(title="Task UUID check")
        self.assertIsNotNone(task.id)


class TaskModelDefaultsTestCase(TestCase):
    """M-02: Default values on new Task."""

    def setUp(self):
        self.task = Task.objects.create(title="Minimal task")

    def test_m02_default_priority_is_medium(self):
        self.assertEqual(self.task.priority, "medium")

    def test_m02_default_status_is_todo(self):
        self.assertEqual(self.task.status, "TODO")

    def test_m02_default_description_is_empty_string(self):
        self.assertEqual(self.task.description, "")

    def test_m02_default_tags_is_empty_list(self):
        self.assertEqual(self.task.tags, [])

    def test_m02_deleted_at_is_none(self):
        self.assertIsNone(self.task.deleted_at)

    def test_m02_created_at_is_set(self):
        self.assertIsNotNone(self.task.created_at)

    def test_m02_due_date_defaults_to_none(self):
        self.assertIsNone(self.task.due_date)


class TaskAliveManagerTestCase(TestCase):
    """M-03: AliveManager excludes soft-deleted tasks."""

    def setUp(self):
        self.alive = Task.objects.create(title="Alive task")
        self.soft_deleted = Task.all_objects.create(title="Deleted task")
        # Soft-delete by setting deleted_at directly
        self.soft_deleted.deleted_at = timezone.now()
        self.soft_deleted.save(update_fields=["deleted_at"])

    def test_m03_alive_manager_excludes_soft_deleted(self):
        """Task.objects should not include soft-deleted rows."""
        qs = Task.objects.all()
        self.assertEqual(qs.count(), 1)
        self.assertIn(self.alive, qs)
        self.assertNotIn(self.soft_deleted, qs)

    def test_m03_alive_manager_count_is_one(self):
        self.assertEqual(Task.objects.count(), 1)


class TaskAllObjectsManagerTestCase(TestCase):
    """M-04: all_objects manager includes soft-deleted tasks."""

    def setUp(self):
        self.alive = Task.all_objects.create(title="Alive task")
        self.soft_deleted = Task.all_objects.create(title="Deleted task")
        self.soft_deleted.deleted_at = timezone.now()
        self.soft_deleted.save(update_fields=["deleted_at"])

    def test_m04_all_objects_includes_soft_deleted(self):
        """Task.all_objects should return all rows including soft-deleted."""
        qs = Task.all_objects.all()
        self.assertEqual(qs.count(), 2)
        self.assertIn(self.alive, qs)
        self.assertIn(self.soft_deleted, qs)


class TaskTagsTestCase(TestCase):
    """M-05: Tags deduplication behavior."""

    def test_m05_model_stores_tags_as_given(self):
        """
        Tags dedup happens at the serializer level.
        The model stores whatever is passed — we verify the model itself stores data faithfully.
        If dedup were at model level (e.g. via save()), we'd verify dedup here.
        Since the design puts dedup in the serializer, we test that the model stores what it's given.
        """
        task = Task.objects.create(title="Tag test", tags=["a", "b", "a"])
        # Refresh from DB
        task.refresh_from_db()
        # The model stores what it's given (dedup is done by serializer)
        self.assertIn("a", task.tags)
        self.assertIn("b", task.tags)

    def test_m05_unique_tags_stored_correctly(self):
        """Tags without duplicates are stored as-is."""
        task = Task.objects.create(title="Tag test unique", tags=["x", "y", "z"])
        task.refresh_from_db()
        self.assertEqual(task.tags, ["x", "y", "z"])

    def test_m05_empty_tags_stored_correctly(self):
        """Empty tags list is stored and returned as []."""
        task = Task.objects.create(title="No tags task", tags=[])
        task.refresh_from_db()
        self.assertEqual(task.tags, [])
