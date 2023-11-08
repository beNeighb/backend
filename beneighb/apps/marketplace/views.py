from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated

from apps.marketplace.models import Task
from apps.marketplace.serializers import TaskSerializer


class TaskView(generics.CreateAPIView, generics.RetrieveAPIView):
    queryset = Task.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskSerializer
