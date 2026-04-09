from django.db import models


class AliveManager(models.Manager):
    """Default manager that excludes soft-deleted tasks."""

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)
