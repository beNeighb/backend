from datetime import datetime, timedelta, timezone
from unittest import mock

from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.exceptions import ErrorDetail

from apps.chat.models import Chat, Message
from apps.chat.factories import ChatFactory
from apps.users.factories import UserWithProfileFactory
from apps.marketplace.tests.utils import get_client_with_valid_token


class CreateMessageTestCase(TestCase):
    url_template = '/chats/{}/messages/'

    @classmethod
    def setUpTestData(cls):
        cls.USER = UserWithProfileFactory()
        chat = ChatFactory(assignment__offer__helper=cls.USER.profile)
        cls.url = cls.url_template.format(chat.id)

    def _get_correct_data(self):
        data = {
            'text': 'Hello world',
        }

        datetime_option = datetime.now(tz=timezone.utc) + timedelta(days=1)
        data['sent_at'] = [datetime_option]

        return data

    def test_returns_401_without_token(self):
        client = APIClient()

        data = self._get_correct_data()
        url = self.url_template.format(42)
        response = client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_success_for_helper(self):
        data = self._get_correct_data()

        user = UserWithProfileFactory()
        chat = ChatFactory(assignment__offer__helper=user.profile)
        url = self.url_template.format(chat.id)

        client = get_client_with_valid_token(user)

        response = client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Message.objects.count(), 1)
        message = Message.objects.first()

        expected_data = {
            'id': message.id,
            'chat': message.chat.id,
            'sent_at': mock.ANY,
            'read_at': None,
            'is_mine': True,
            'text': data['text'],
        }
        self.assertEqual(response.data, expected_data)

    def test_success_for_owner(self):
        data = self._get_correct_data()

        user = UserWithProfileFactory()
        chat = ChatFactory(assignment__offer__task__owner=user.profile)

        client = get_client_with_valid_token(user)

        url = self.url_template.format(chat.id)
        response = client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Message.objects.count(), 1)
        message = Message.objects.first()

        expected_data = {
            'id': message.id,
            'chat': message.chat.id,
            'sent_at': mock.ANY,
            'read_at': None,
            'is_mine': True,
            'text': data['text'],
        }
        self.assertEqual(response.data, expected_data)

    def test_user_without_permissions(self):
        data = self._get_correct_data()

        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        response = client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data,
            {
                'detail': ErrorDetail(
                    string='You do not have permission to perform this action.',  # noqa
                    code='permission_denied',
                )
            },
        )

        self.assertEqual(Message.objects.count(), 0)

    def test_incorrect_chat_id(self):
        data = self._get_correct_data()

        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        non_existent_chat_id = 42
        self.assertFalse(Chat.objects.filter(id=non_existent_chat_id).exists())

        url = self.url_template.format(42)
        response = client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(Message.objects.count(), 0)

    def test_requires_correct_sent_at(self):
        data = self._get_correct_data()
        data['sent_at'] = 'not a datetime'

        client = get_client_with_valid_token(self.USER)

        response = client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Message.objects.count(), 0)

    def test_requires_text(self):
        data = self._get_correct_data()
        del data['text']

        client = get_client_with_valid_token(self.USER)

        response = client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Message.objects.count(), 0)

    def test_requires_text_to_be_non_empty(self):
        data = self._get_correct_data()
        data['text'] = ''

        client = get_client_with_valid_token(self.USER)

        response = client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Message.objects.count(), 0)

    def test_requires_text_to_be_less_than_300_chars(self):
        data = self._get_correct_data()
        data['text'] = 'a' * 301

        client = get_client_with_valid_token(self.USER)

        response = client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                'text': [
                    ErrorDetail(
                        string='Ensure this field has no more than 300 characters.',  # noqa
                        code='max_length',
                    )
                ]
            },
        )

        self.assertEqual(Message.objects.count(), 0)
