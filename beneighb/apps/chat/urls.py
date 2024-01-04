from django.urls import path

from apps.chat.views import ChatMineListView, MessageCreateView


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
]
