import logging


from rest_framework import generics
from rest_framework.permissions import BasePermission, IsAuthenticated

from apps.chat.models import Chat, Message
from apps.chat.serializers import MessageSerializer

logger = logging.getLogger(__name__)


# TODO: Move to permissions.py
class ChatAccessPermissionClass(BasePermission):
    def has_permission(self, request, view):
        chat_id = view.kwargs['chat_id']
        chat = Chat.objects.filter(id=chat_id).first()

        if not chat:
            from django.http import Http404

            raise Http404('Chat not found')

        my_profile = request.user.profile
        chat_authors = [
            chat.assignment.offer.helper,
            chat.assignment.offer.task.owner,
        ]

        return my_profile in chat_authors


class MessageCreateView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, ChatAccessPermissionClass)
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
