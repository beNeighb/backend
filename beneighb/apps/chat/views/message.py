import logging

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .permissions import (
    ChatAccessPermissionClass,
    MessageAccessPermissionClass,
)

from apps.chat.models import Message
from apps.chat.serializers import (
    MessageMarkAsReadSerializer,
    MessageSerializer,
)

logger = logging.getLogger(__name__)


class MessageCreateView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, ChatAccessPermissionClass)
    serializer_class = MessageSerializer
    queryset = Message.objects.all()


class MessageMarkAsReadView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, MessageAccessPermissionClass)
    serializer_class = MessageMarkAsReadSerializer
    lookup_url_kwarg = 'message_id'
    queryset = Message.objects.all()
