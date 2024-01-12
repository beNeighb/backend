from rest_framework.permissions import IsAuthenticated

from rest_framework import generics, status
from rest_framework.exceptions import APIException

from apps.users.models import Profile
from apps.users.serializers import ProfileSerializer, ShortProfileSerializer


# TODO: Move to exceptions.py when we have more
class UserProfileExistException(APIException):
    status_code = status.HTTP_409_CONFLICT


class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ShortProfileSerializer
    queryset = Profile.objects.all()

    def delete(self, request, *args, **kwargs):
        profile = self.get_object()

        if profile.user != request.user:
            from django.http import HttpResponseBadRequest

            return HttpResponseBadRequest(
                "You can't delete other user's profile"
            )

        return super().delete(request, *args, **kwargs)


class MyProfileView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer

    def get_object(self):
        user = self.request.user
        if user.profile:
            return user.profile

        from django.http import Http404

        raise Http404("User doesn't have a profile yet")


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
