from rest_framework.permissions import IsAuthenticated

from rest_framework import generics, status
from rest_framework.exceptions import APIException

from apps.users.models import Profile
from apps.users.serializers import ProfileSerializer


# TODO: Move to exceptions.py when we have more
class UserProfileExistException(APIException):
    status_code = status.HTTP_409_CONFLICT


class ProfileCreateView(generics.CreateAPIView):
    queryset = Profile.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer

    def perform_create(self, serializer):
        user = self.request.user

        if user.profile:
            raise UserProfileExistException(
                'Profile for this user already exists'
            )

        profile = serializer.save()
        profile.user = user

        # Save the profile
        user.save()
