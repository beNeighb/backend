from django.urls import path

from apps.chat.views import (
    ChatMineListView,
    MessageCreateView,
    MessageMarkAsReadView,
)


urlpatterns = [
    path(
        '',
        ChatMineListView.as_view(),
        name='chats-mine',
    ),
    path(
        '<int:chat_id>/messages/',
        MessageCreateView.as_view(),
        name='message-create',
    ),
    path(
        'messages/<int:message_id>/mark-as-read/',
        MessageMarkAsReadView.as_view(),
        name='message-read',
    ),
]
