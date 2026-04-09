import django_filters
from tasks.models import Task, STATUS_CHOICES, PRIORITY_CHOICES


class TaskFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=STATUS_CHOICES)
    priority = django_filters.ChoiceFilter(choices=PRIORITY_CHOICES)

    class Meta:
        model = Task
        fields = ["status", "priority"]

    @property
    def qs(self):
        """Raise 400 if filter values are invalid."""
        if not self.is_valid():
            from rest_framework.exceptions import ValidationError
            raise ValidationError(self.errors)
        return super().qs
