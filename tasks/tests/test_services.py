"""
Unit tests for the transition_status service function.
Pure function tests — no database, no HTTP.
Uses SimpleTestCase (no DB setup overhead).
"""
from django.test import SimpleTestCase
from rest_framework.exceptions import ValidationError

from tasks.services import transition_status


class TransitionStatusValidTransitionsTestCase(SimpleTestCase):
    """Tests for the 4 valid transitions in the state machine matrix."""

    def test_todo_forward_returns_in_progress(self):
        result = transition_status("TODO", "forward")
        self.assertEqual(result, "IN_PROGRESS")

    def test_in_progress_forward_returns_done(self):
        result = transition_status("IN_PROGRESS", "forward")
        self.assertEqual(result, "DONE")

    def test_in_progress_backward_returns_todo(self):
        result = transition_status("IN_PROGRESS", "backward")
        self.assertEqual(result, "TODO")

    def test_done_backward_returns_in_progress(self):
        result = transition_status("DONE", "backward")
        self.assertEqual(result, "IN_PROGRESS")


class TransitionStatusInvalidTransitionsTestCase(SimpleTestCase):
    """Tests for the 2 invalid transitions (boundary violations)."""

    def test_todo_backward_raises_validation_error(self):
        """TODO has no previous state — backward transition is invalid."""
        with self.assertRaises(ValidationError) as ctx:
            transition_status("TODO", "backward")
        exc = ctx.exception
        # DRF ValidationError stores per-field codes in get_codes(), not default_code.
        # We verify the code is 'invalid_transition' via get_codes().
        codes = exc.get_codes()
        # codes is {'direction': ['invalid_transition']}
        all_codes = []
        if isinstance(codes, dict):
            for v in codes.values():
                if isinstance(v, list):
                    all_codes.extend(v)
                else:
                    all_codes.append(v)
        elif isinstance(codes, list):
            all_codes = codes
        else:
            all_codes = [codes]
        self.assertIn("invalid_transition", all_codes)

    def test_done_forward_raises_validation_error(self):
        """DONE has no next state — forward transition is invalid."""
        with self.assertRaises(ValidationError) as ctx:
            transition_status("DONE", "forward")
        exc = ctx.exception
        codes = exc.get_codes()
        all_codes = []
        if isinstance(codes, dict):
            for v in codes.values():
                if isinstance(v, list):
                    all_codes.extend(v)
                else:
                    all_codes.append(v)
        elif isinstance(codes, list):
            all_codes = codes
        else:
            all_codes = [codes]
        self.assertIn("invalid_transition", all_codes)

    def test_todo_backward_error_details_reference_direction(self):
        """Error detail should be a dict with 'direction' key."""
        with self.assertRaises(ValidationError) as ctx:
            transition_status("TODO", "backward")
        exc = ctx.exception
        self.assertIsInstance(exc.detail, dict)
        self.assertIn("direction", exc.detail)

    def test_done_forward_error_details_reference_direction(self):
        """Error detail should be a dict with 'direction' key."""
        with self.assertRaises(ValidationError) as ctx:
            transition_status("DONE", "forward")
        exc = ctx.exception
        self.assertIsInstance(exc.detail, dict)
        self.assertIn("direction", exc.detail)
