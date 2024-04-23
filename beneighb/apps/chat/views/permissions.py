import logging

from rest_framework.permissions import BasePermission

from apps.chat.models import Chat, Message


logger = logging.getLogger(__name__)


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


class MessageAccessPermissionClass(BasePermission):
    def has_permission(self, request, view):
        message_id = view.kwargs['message_id']
        message = Message.objects.filter(id=message_id).first()

        if not message:
            from django.http import Http404

            raise Http404('Message not found')

        my_profile = request.user.profile
        chat = message.chat
        chat_authors = [
            chat.offer.helper,
            chat.offer.task.owner,
        ]

        return my_profile in chat_authors
