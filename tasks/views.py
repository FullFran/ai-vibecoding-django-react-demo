from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from tasks.models import Task
from tasks.serializers import TaskSerializer, TransitionSerializer
from tasks.services import transition_status
from tasks.filters import TaskFilter


class TaskPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()   # AliveManager — soft-deleted excluded
    serializer_class = TaskSerializer
    pagination_class = TaskPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def destroy(self, request, *args, **kwargs):
        """Soft delete: set deleted_at instead of physical deletion."""
        task = self.get_object()
        task.deleted_at = timezone.now()
        task.save(update_fields=["deleted_at", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="transition")
    def transition(self, request, pk=None):
        """Advance or revert the task status by one step."""
        task = self.get_object()
        serializer = TransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        direction = serializer.validated_data["direction"]

        new_status = transition_status(task.status, direction)
        task.status = new_status
        task.save(update_fields=["status", "updated_at"])

        return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)
