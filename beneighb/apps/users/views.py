from rest_framework import generics
from django.shortcuts import get_object_or_404


from apps.users.models import Profile, User
from apps.users.serializers import ProfileSerializer


class ProfileCreateView(generics.CreateAPIView):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def perform_create(self, serializer):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)

        profile = serializer.save()
        profile.user = user

        # Save the profile
        user.save()
