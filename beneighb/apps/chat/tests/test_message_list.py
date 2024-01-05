from unittest import mock
from collections import OrderedDict

from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from apps.chat.factories import ChatFactory, MessageFactory
from apps.users.factories import UserWithProfileFactory
from apps.marketplace.tests.utils import get_client_with_valid_token
from apps.chat.models import Chat


class MessageListTestCase(TestCase):
    url_template = '/chats/{}/messages/'

    @classmethod
    def setUpTestData(cls):
        cls.USER = UserWithProfileFactory()
        cls.CHAT = ChatFactory(assignment__offer__helper=cls.USER.profile)
        cls.MESSAGE = MessageFactory(chat=cls.CHAT, author=cls.USER.profile)
        cls.URL = cls.url_template.format(cls.CHAT.id)

    def test_returns_401_without_token(self):
        client = APIClient()

        response = client.get(self.URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_success_for_helper(self):
        client = get_client_with_valid_token(self.USER)

        message_2 = MessageFactory(  # noqa
            chat=self.CHAT, author=self.USER.profile
        )

        response = client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_success_for_owner(self):
        user = UserWithProfileFactory()
        chat = ChatFactory(assignment__offer__task__owner=user.profile)
        for i in range(5):
            MessageFactory(chat=chat, author=user.profile)

        url = self.url_template.format(chat.id)

        client = get_client_with_valid_token(user)

        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)

    def test_respects_limit_query_param(self):
        user = UserWithProfileFactory()
        chat = ChatFactory(assignment__offer__task__owner=user.profile)
        for i in range(5):
            MessageFactory(chat=chat, author=user.profile)

        url = self.url_template.format(chat.id) + '?limit=3'

        client = get_client_with_valid_token(user)

        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_invalid_limit_query_param(self):
        user = UserWithProfileFactory()
        chat = ChatFactory(assignment__offer__task__owner=user.profile)
        for i in range(5):
            MessageFactory(chat=chat, author=user.profile)

        client = get_client_with_valid_token(user)

        for limit in ['a', '']:
            url = self.url_template.format(chat.id) + '?limit={limit}'

            response = client.get(url)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.data,
                {'error': 'Invalid limit value. Must be an integer.'},
            )

    def test_success_correct_fields_for_msg(self):
        client = get_client_with_valid_token(self.USER)

        response = client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_msg = OrderedDict(
            {
                'id': self.MESSAGE.id,
                'chat': self.MESSAGE.chat.id,
                'sent_at': mock.ANY,
                'read_at': None,
                'is_mine': True,
                'text': self.MESSAGE.text,
            }
        )

        self.assertEqual(
            response.data[0],
            expected_msg,
        )

    def test_returns_404_for_non_existing_chat(self):
        client = get_client_with_valid_token(self.USER)

        fake_chat_id = 42
        self.assertEqual(Chat.objects.filter(id=fake_chat_id).exists(), False)
        url = self.url_template.format(fake_chat_id)

        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_returns_403_for_non_participant(self):
        user = UserWithProfileFactory()

        client = get_client_with_valid_token(user)

        response = client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
