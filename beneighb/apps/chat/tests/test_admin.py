from django.test import TestCase
from django.contrib.admin.sites import AdminSite

from apps.chat.admin import ChatAdmin
from apps.chat.models import Chat
from apps.chat.factories import ChatFactory


class TestChatAdmin(TestCase):
    def test_get_task_owner(self):
        chat = ChatFactory()
        chat_admin = ChatAdmin(model=Chat, admin_site=AdminSite())
        assert chat_admin.get_task_owner(chat) == chat.offer.task.owner

    def test_get_offer_helper(self):
        chat = ChatFactory()
        chat_admin = ChatAdmin(model=Chat, admin_site=AdminSite())
        assert chat_admin.get_offer_helper(chat) == chat.offer.helper
