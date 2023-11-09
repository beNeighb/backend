from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated

from apps.marketplace.models import Task
from apps.marketplace.serializers import TaskSerializer


class TaskCreateListView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)


class TaskRetrieveView(generics.RetrieveAPIView):
    queryset = Task.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskSerializer
