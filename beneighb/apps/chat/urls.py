from django.urls import path

from apps.chat.views import ChatMineListView


urlpatterns = [
    path(
        '',
        ChatMineListView.as_view(),
        name='chats-mine',
    ),
]
