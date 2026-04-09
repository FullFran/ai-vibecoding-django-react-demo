import uuid
from django.db import models
from tasks.managers import AliveManager

PRIORITY_CHOICES = [
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
]

STATUS_CHOICES = [
    ("TODO", "To Do"),
    ("IN_PROGRESS", "In Progress"),
    ("DONE", "Done"),
]


class Task(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="medium",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="TODO",
    )
    due_date = models.DateField(null=True, blank=True)
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Default manager filters out soft-deleted rows
    objects = AliveManager()
    # Escape hatch for admin / migrations / raw access
    all_objects = models.Manager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["status"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["deleted_at"]),
            models.Index(fields=["deleted_at", "created_at"]),
        ]

    def __str__(self):
        return self.title
