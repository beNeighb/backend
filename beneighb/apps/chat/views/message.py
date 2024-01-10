import logging

from django.db.models import Q

from rest_framework import generics, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .permissions import (
    ChatAccessPermissionClass,
    MessageAccessPermissionClass,
)

from apps.chat.models import Chat, Message
from apps.chat.serializers import (
    MessageCreateSerializer,
    MessageMarkAsReadSerializer,
    MessageSerializer,
)


logger = logging.getLogger(__name__)


class UnreadMessageList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = MessageSerializer

    def list(self, request, *args, **kwargs):
        unread = self.request.query_params.get('unread', None)
        if unread != 'true':
            return Response(
                {'error': 'Invalid unread value. Must be "true"'},
                status=400,
            )

        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        my_profile = self.request.user.profile

        # TODO: Move to utils
        is_helper = Q(assignment__offer__helper=my_profile)
        is_owner = Q(assignment__offer__task__owner=my_profile)

        my_chats = Chat.objects.filter(is_helper | is_owner)

        return Message.objects.filter(
            chat__in=my_chats,
            read_at__isnull=True,
        ).exclude(author=my_profile)


class MessageMarkAsReadView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, MessageAccessPermissionClass)
    serializer_class = MessageMarkAsReadSerializer
    lookup_url_kwarg = 'message_id'
    queryset = Message.objects.all()


class MessageForChatViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ChatAccessPermissionClass]

    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        else:
            return MessageSerializer

    def get_queryset(self):
        chat_id = self.kwargs.get('chat_id')
        return Message.objects.filter(chat_id=chat_id)

    def list(self, request, chat_id=None):
        queryset = self.get_queryset()

        limit = request.query_params.get('limit', None)
        if limit is not None:
            try:
                limit = int(limit)
            except ValueError:
                return Response(
                    {'error': 'Invalid limit value. Must be an integer.'},
                    status=400,
                )

            queryset = queryset[:limit]

        serializer = MessageSerializer(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data)
