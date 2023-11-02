from django.shortcuts import render
from rest_framework import generics, status

from apps.marketplace.serializers import TaskSerializer

# Create your views here.


class TaskCreateView(generics.CreateAPIView):
    # queryset = Profile.objects.all()
    # permission_classes = (IsAuthenticated,)
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
