import logging

from django.db.models import Q

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.chat.models import Chat
from apps.chat.serializers import ChatWithMessageDataSerializer

logger = logging.getLogger(__name__)


class ChatMineListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChatWithMessageDataSerializer

    def get_queryset(self):
        my_profile = self.request.user.profile

        is_helper = Q(assignment__offer__helper=my_profile)
        is_owner = Q(assignment__offer__task__owner=my_profile)

        qs = Chat.objects.filter(is_helper | is_owner)
        limit = self.request.query_params.get('limit', None)
        if limit:
            qs = qs[: int(limit)]

        return qs
