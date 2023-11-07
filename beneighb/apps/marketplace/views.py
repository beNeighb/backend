from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated

from apps.marketplace.models import Task
from apps.marketplace.serializers import TaskSerializer


class TaskCreateView(generics.CreateAPIView):
    queryset = Task.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskSerializer
