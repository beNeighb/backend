from datetime import datetime, timedelta, timezone
from unittest import mock

from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.exceptions import ErrorDetail

from apps.chat.factories import ChatFactory, MessageFactory
from apps.users.factories import UserWithProfileFactory
from apps.marketplace.tests.utils import get_client_with_valid_token


class MessageMarkAsReadTestCase(TestCase):
    url_template = '/chats/messages/{}/mark-as-read/'

    @classmethod
    def setUpTestData(cls):
        cls.USER = UserWithProfileFactory()
        chat = ChatFactory(assignment__offer__helper=cls.USER.profile)
        cls.MESSAGE = MessageFactory(chat=chat)
        cls.URL = cls.url_template.format(cls.MESSAGE.id)

    def _get_correct_data(self):
        data = {}
        datetime_option = datetime.now(tz=timezone.utc) + timedelta(days=1)
        data['read_at'] = [datetime_option]

        return data

    def test_returns_401_without_token(self):
        client = APIClient()

        data = self._get_correct_data()
        response = client.put(self.URL, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_success_for_helper(self):
        data = self._get_correct_data()
        client = get_client_with_valid_token(self.USER)

        response = client.put(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.MESSAGE.refresh_from_db()
        self.assertIsNotNone(self.MESSAGE.read_at)

        self.assertEqual(
            response.data,
            {'id': self.MESSAGE.id, 'read_at': mock.ANY},
        )

    def test_success_for_owner(self):
        data = self._get_correct_data()

        user = UserWithProfileFactory()
        chat = ChatFactory(assignment__offer__task__owner=user.profile)
        message = MessageFactory(chat=chat)
        url = self.url_template.format(message.id)

        client = get_client_with_valid_token(user)

        response = client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        message.refresh_from_db()
        self.assertIsNotNone(message.read_at)

        self.assertEqual(
            response.data,
            {'id': message.id, 'read_at': mock.ANY},
        )

    def test_marks_all_messages_before_given_as_read(self):
        task_owner = UserWithProfileFactory().profile
        chat = ChatFactory(assignment__offer__task__owner=task_owner)

        offer_helper = chat.assignment.offer.helper
        # Hack: offer_helper.user for some reason loses its profile
        offer_helper.user.save()

        message_1 = MessageFactory(chat=chat, author=task_owner)
        message_2 = MessageFactory(chat=chat, author=task_owner)
        message_3 = MessageFactory(chat=chat, author=task_owner)

        url = self.url_template.format(message_2.id)

        data = self._get_correct_data()
        client = get_client_with_valid_token(offer_helper.user)

        response = client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        message_1.refresh_from_db()
        self.assertIsNotNone(message_1.read_at)

        message_2.refresh_from_db()
        self.assertIsNotNone(message_2.read_at)

        message_3.refresh_from_db()
        self.assertIsNone(message_3.read_at)

    def test_returns_404_for_non_existing_message(self):
        data = self._get_correct_data()
        client = get_client_with_valid_token(self.USER)

        url = self.url_template.format(self.MESSAGE.id + 1)

        response = client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_returns_403_for_non_participant(self):
        data = self._get_correct_data()

        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        response = client.put(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_returns_400_for_invalid_data(self):
        data = self._get_correct_data()
        data['read_at'] = ['invalid date']

        client = get_client_with_valid_token(self.USER)

        response = client.put(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            response.data,
            {
                'read_at': [
                    ErrorDetail(
                        string='Datetime has wrong format. Use one of these '
                        'formats instead: '
                        'YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z].',
                        code='invalid',
                    ),
                ],
            },
        )

    def test_returns_400_for_request_without_read_at(self):
        data = {}

        client = get_client_with_valid_token(self.USER)

        response = client.put(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            response.data,
            {
                'read_at': [
                    ErrorDetail(
                        string="Field 'read_at' cannot be missing or empty.",
                        code='invalid',
                    )
                ]
            },
        )

    def test_doesnt_update_already_read_message(self):
        data = self._get_correct_data()

        client = get_client_with_valid_token(self.USER)

        response = client.put(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_read_at = response.data['read_at']

        data = self._get_correct_data()

        response = client.put(self.URL, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['read_at'], response_read_at)
