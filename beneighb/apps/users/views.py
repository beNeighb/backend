from django.db.models import Q
from django.http.response import HttpResponseBadRequest, HttpResponse

from rest_framework.permissions import IsAuthenticated

from rest_framework import generics, status
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from apps.chat.models import Chat
from apps.users.models import Block, Profile
from apps.users.serializers import (
    ProfileSerializer,
    ShortProfileSerializer,
    ProfileWithFcmTokenSerializer,
)


# TODO: Move to exceptions.py when we have more
class UserProfileExistException(APIException):
    status_code = status.HTTP_409_CONFLICT


# TODO: Move to exceptions.py when we have more
class HttpForbiddenException(APIException):
    status_code = status.HTTP_403_FORBIDDEN


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


class MyProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method in ['PATCH']:
            return ProfileWithFcmTokenSerializer
        return ProfileSerializer

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


# TODO: Move to utils
class HttpResponseConflict(HttpResponse):
    status_code = 409


class ProfileBlockView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        profile = self.get_object()

        if profile.user == request.user:
            return HttpResponseBadRequest('You can\'t block yourself')

        blocked_profile = profile
        blocking_profile = request.user.profile

        exists = Block.objects.filter(
            blocked_profile=blocked_profile, blocking_profile=blocking_profile
        ).exists()

        if exists:
            return HttpResponseConflict('You already blocked this user')

        Block.objects.create(
            blocked_profile=blocked_profile, blocking_profile=blocking_profile
        )

        self._delete_blocked_chats(blocking_profile, blocked_profile)
        self._delete_blocked_offers(blocking_profile, blocked_profile)

        return self.get_response()

    def get_object(self):
        profile_id = self.kwargs.get('pk')
        try:
            return Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            from django.http import Http404

            raise Http404("Profile doesn't exist")

    def get_response(self):
        return Response(status=status.HTTP_200_OK)

    def _delete_blocked_offers(self, blocking_profile, blocked_profile):
        blocked_profile.offers.filter(task__owner=blocking_profile).delete()
        blocking_profile.offers.filter(task__owner=blocked_profile).delete()

    def _delete_blocked_chats(self, blocking_profile, blocked_profile):
        # TODO: Room to improvement performance
        chats_to_delete = Chat.objects.filter(
            Q(
                offer__helper=blocked_profile,
                offer__task__owner=blocking_profile,
            )
            | Q(  # noqa - conflict with black
                offer__helper=blocking_profile,
                offer__task__owner=blocked_profile,
            )
        )
        chats_to_delete.delete()
