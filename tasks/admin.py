from django.contrib import admin
from tasks.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "priority", "created_at", "deleted_at"]
    list_filter = ["status", "priority"]

    def get_queryset(self, request):
        return Task.all_objects.all()
