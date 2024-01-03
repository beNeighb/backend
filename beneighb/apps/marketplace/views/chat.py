import logging

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.marketplace.models import Chat
from apps.marketplace.serializers import ChatSerializer

logger = logging.getLogger(__name__)


class ChatMineListView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChatSerializer

    def get_queryset(self):
        my_profile = self.request.user.profile

        from django.db.models import Q

        is_helper = Q(assignment__offer__helper=my_profile)
        is_owner = Q(assignment__offer__task__owner=my_profile)

        return Chat.objects.filter(is_helper | is_owner)
