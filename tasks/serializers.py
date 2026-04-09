from rest_framework import serializers
from tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "id", "title", "description", "priority", "status",
            "due_date", "tags", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "status", "created_at", "updated_at"]

    def validate_title(self, value):
        """Trim whitespace, enforce 3-200 char length."""
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError(
                "Title must be at least 3 characters after trimming."
            )
        if len(value) > 200:
            raise serializers.ValidationError(
                "Title must not exceed 200 characters."
            )
        return value

    def validate_tags(self, value):
        """Ensure tags is a list of strings, deduplicate preserving order."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Tags must be a list.")
        for tag in value:
            if not isinstance(tag, str):
                raise serializers.ValidationError(
                    "Each tag must be a string."
                )
        # Dedup preserving insertion order
        return list(dict.fromkeys(value))


class TransitionSerializer(serializers.Serializer):
    DIRECTION_CHOICES = [("forward", "Forward"), ("backward", "Backward")]

    direction = serializers.ChoiceField(choices=DIRECTION_CHOICES)
