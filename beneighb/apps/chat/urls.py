from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.chat.views import (
    ChatMineListView,
    MessageMarkAsReadView,
    MessageForChatViewSet,
)

router = DefaultRouter()
router.register(r'messages', MessageForChatViewSet, basename='message')

urlpatterns = [
    path(
        '',
        ChatMineListView.as_view(),
        name='chats-mine',
    ),
    path('<int:chat_id>/', include(router.urls)),
    path(
        'messages/<int:message_id>/mark-as-read/',
        MessageMarkAsReadView.as_view(),
        name='message-read',
    ),
]
