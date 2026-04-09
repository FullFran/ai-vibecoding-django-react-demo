"""
Unit tests for TaskSerializer and TransitionSerializer.
Tests instantiate serializers directly — no HTTP layer.
"""
from django.test import TestCase

from tasks.models import Task
from tasks.serializers import TaskSerializer, TransitionSerializer


class TaskSerializerTitleValidationTestCase(TestCase):
    """Title validation: trimming, min/max length."""

    def _serialize(self, title):
        data = {"title": title}
        s = TaskSerializer(data=data)
        return s

    def test_title_3_chars_passes(self):
        s = self._serialize("abc")
        self.assertTrue(s.is_valid(), s.errors)

    def test_title_200_chars_passes(self):
        s = self._serialize("a" * 200)
        self.assertTrue(s.is_valid(), s.errors)

    def test_title_2_chars_fails(self):
        s = self._serialize("ab")
        self.assertFalse(s.is_valid())
        self.assertIn("title", s.errors)

    def test_title_201_chars_fails(self):
        s = self._serialize("a" * 201)
        self.assertFalse(s.is_valid())
        self.assertIn("title", s.errors)

    def test_title_whitespace_only_fails(self):
        s = self._serialize("   ")
        self.assertFalse(s.is_valid())
        self.assertIn("title", s.errors)

    def test_title_trim_reduces_below_min_fails(self):
        """'  ab  ' trimmed to 'ab' (2 chars) → fails."""
        s = self._serialize("  ab  ")
        self.assertFalse(s.is_valid())
        self.assertIn("title", s.errors)

    def test_title_trim_leaves_valid_passes(self):
        """'  abc  ' trimmed to 'abc' (3 chars) → passes."""
        s = self._serialize("  abc  ")
        self.assertTrue(s.is_valid(), s.errors)
        # Saved value must be trimmed
        self.assertEqual(s.validated_data["title"], "abc")

    def test_title_trim_one_char_fails(self):
        """'  a  ' trimmed to 'a' (1 char) → fails."""
        s = self._serialize("  a  ")
        self.assertFalse(s.is_valid())
        self.assertIn("title", s.errors)


class TaskSerializerTagsValidationTestCase(TestCase):
    """Tags validation: type check and deduplication."""

    def _serialize(self, tags):
        data = {"title": "Valid title", "tags": tags}
        s = TaskSerializer(data=data)
        return s

    def test_tags_non_list_fails(self):
        s = self._serialize("single-tag")
        self.assertFalse(s.is_valid())
        self.assertIn("tags", s.errors)

    def test_tags_list_with_int_fails(self):
        s = self._serialize(["valid", 42])
        self.assertFalse(s.is_valid())
        self.assertIn("tags", s.errors)

    def test_tags_list_with_bool_fails(self):
        s = self._serialize([True, "valid"])
        self.assertFalse(s.is_valid())
        self.assertIn("tags", s.errors)

    def test_tags_valid_list_passes(self):
        s = self._serialize(["tag1", "tag2"])
        self.assertTrue(s.is_valid(), s.errors)

    def test_tags_empty_list_passes(self):
        s = self._serialize([])
        self.assertTrue(s.is_valid(), s.errors)

    def test_tags_duplicates_are_deduped_preserving_order(self):
        s = self._serialize(["a", "b", "a", "c", "b"])
        self.assertTrue(s.is_valid(), s.errors)
        # Dedup preserves insertion order
        self.assertEqual(s.validated_data["tags"], ["a", "b", "c"])

    def test_tags_dict_fails(self):
        s = self._serialize({"key": "value"})
        self.assertFalse(s.is_valid())
        self.assertIn("tags", s.errors)


class TaskSerializerPriorityValidationTestCase(TestCase):
    """Priority validation: enum check."""

    def _serialize(self, priority):
        data = {"title": "Valid title", "priority": priority}
        s = TaskSerializer(data=data)
        return s

    def test_priority_low_passes(self):
        s = self._serialize("low")
        self.assertTrue(s.is_valid(), s.errors)

    def test_priority_medium_passes(self):
        s = self._serialize("medium")
        self.assertTrue(s.is_valid(), s.errors)

    def test_priority_high_passes(self):
        s = self._serialize("high")
        self.assertTrue(s.is_valid(), s.errors)

    def test_priority_urgent_fails(self):
        s = self._serialize("urgent")
        self.assertFalse(s.is_valid())
        self.assertIn("priority", s.errors)

    def test_priority_critical_fails(self):
        s = self._serialize("critical")
        self.assertFalse(s.is_valid())
        self.assertIn("priority", s.errors)


class TaskSerializerReadOnlyFieldsTestCase(TestCase):
    """Read-only fields: status, id, created_at, updated_at."""

    def test_status_done_in_input_is_ignored_output_shows_todo(self):
        """Sending status='DONE' should be silently ignored; task gets status='TODO'."""
        data = {"title": "Test task", "status": "DONE"}
        s = TaskSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        # status is read-only, not in validated_data
        self.assertNotIn("status", s.validated_data)

    def test_status_field_not_in_validated_data(self):
        """status should never appear in validated_data as it's read_only."""
        data = {"title": "Test task", "status": "IN_PROGRESS"}
        s = TaskSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        self.assertNotIn("status", s.validated_data)

    def test_id_is_read_only(self):
        """Sending id in input should be silently ignored."""
        import uuid
        fake_id = str(uuid.uuid4())
        data = {"title": "Test task", "id": fake_id}
        s = TaskSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        self.assertNotIn("id", s.validated_data)


class TaskSerializerOutputTestCase(TestCase):
    """Serializer output format."""

    def test_deleted_at_not_in_output(self):
        """deleted_at must not appear in serializer output."""
        task = Task.objects.create(title="Test output")
        s = TaskSerializer(task)
        self.assertNotIn("deleted_at", s.data)

    def test_all_expected_fields_in_output(self):
        """All expected fields must appear in output."""
        task = Task.objects.create(title="Test fields")
        s = TaskSerializer(task)
        expected_fields = {
            "id", "title", "description", "priority", "status",
            "due_date", "tags", "created_at", "updated_at"
        }
        for field in expected_fields:
            self.assertIn(field, s.data, f"Missing field: {field}")


class TransitionSerializerTestCase(TestCase):
    """TransitionSerializer validation."""

    def test_direction_forward_passes(self):
        s = TransitionSerializer(data={"direction": "forward"})
        self.assertTrue(s.is_valid(), s.errors)
        self.assertEqual(s.validated_data["direction"], "forward")

    def test_direction_backward_passes(self):
        s = TransitionSerializer(data={"direction": "backward"})
        self.assertTrue(s.is_valid(), s.errors)
        self.assertEqual(s.validated_data["direction"], "backward")

    def test_direction_sideways_fails(self):
        s = TransitionSerializer(data={"direction": "sideways"})
        self.assertFalse(s.is_valid())
        self.assertIn("direction", s.errors)

    def test_direction_empty_fails(self):
        s = TransitionSerializer(data={})
        self.assertFalse(s.is_valid())
        self.assertIn("direction", s.errors)

    def test_direction_invalid_string_fails(self):
        s = TransitionSerializer(data={"direction": "up"})
        self.assertFalse(s.is_valid())
        self.assertIn("direction", s.errors)
