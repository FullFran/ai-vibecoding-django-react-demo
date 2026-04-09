from rest_framework.exceptions import ValidationError

# State machine matrix: (current_status, direction) → new_status
TRANSITION_MATRIX = {
    ("TODO", "forward"): "IN_PROGRESS",
    ("IN_PROGRESS", "forward"): "DONE",
    ("IN_PROGRESS", "backward"): "TODO",
    ("DONE", "backward"): "IN_PROGRESS",
}


def transition_status(current_status: str, direction: str) -> str:
    """
    Pure function: compute the new status given current status and direction.
    Raises ValidationError if the transition is not allowed.
    """
    key = (current_status, direction)
    new_status = TRANSITION_MATRIX.get(key)
    if new_status is None:
        raise ValidationError(
            {
                "direction": [
                    f"Cannot move '{direction}' from status '{current_status}'."
                ]
            },
            code="invalid_transition",
        )
    return new_status
