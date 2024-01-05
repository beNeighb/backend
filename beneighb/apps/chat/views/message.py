import logging

from rest_framework import generics, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .permissions import (
    ChatAccessPermissionClass,
    MessageAccessPermissionClass,
)

from apps.chat.models import Message
from apps.chat.serializers import (
    MessageCreateSerializer,
    MessageMarkAsReadSerializer,
    MessageSerializer,
)

logger = logging.getLogger(__name__)


class MessageCreateView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, ChatAccessPermissionClass)
    serializer_class = MessageCreateSerializer
    queryset = Message.objects.all()


class MessageListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, ChatAccessPermissionClass)
    serializer_class = MessageSerializer

    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        return Message.objects.filter(chat_id=chat_id)


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
