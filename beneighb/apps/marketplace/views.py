from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated

from apps.marketplace.models import Task
from apps.marketplace.serializers import TaskSerializer


class TaskCreateView(generics.CreateAPIView):
    queryset = Task.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskSerializer

    # def perform_create(self, serializer):
    #     user = self.request.user

    #     if user.profile:
    #         raise UserProfileExistException(
    #             'Profile for this user already exists'
    #         )

    #     profile = serializer.save()
    #     profile.user = user

    #     # Save the profile
    #     user.save()
