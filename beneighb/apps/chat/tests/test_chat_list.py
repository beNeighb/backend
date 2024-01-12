from unittest import mock
from collections import OrderedDict

from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from apps.users.factories import UserWithProfileFactory

from apps.chat.factories import ChatFactory
from apps.users.tests.utils import get_client_with_valid_token


class ChatListTestCase(TestCase):
    url = '/chats/'

    def test_returns_401_without_token(self):
        client = APIClient()

        response = client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_chats_without_chats(self):
        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        url = self.url
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_get_chats(self):
        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        chat_1 = ChatFactory(assignment__offer__helper=user.profile)
        chat_2 = ChatFactory(assignment__offer__helper=user.profile)

        url = self.url
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_chat_ids = set([chat['id'] for chat in response.data])
        expected_chat_ids = set([chat_1.id, chat_2.id])
        self.assertEqual(response_chat_ids, expected_chat_ids)

    def test_get_chats_returns_correct_fields_for_helper(self):
        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        chat = ChatFactory(assignment__offer__helper=user.profile)

        url = self.url
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = OrderedDict(
            {
                'id': chat.id,
                'created_at': mock.ANY,
                'offer': chat.assignment.offer.id,
                'service': chat.assignment.offer.task.service.id,
                'profile_name': chat.assignment.offer.task.owner.name,
            }
        )

        self.assertEqual(response.data[0], expected_data)

    def test_get_chats_returns_correct_fields_for_task_owner(self):
        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        chat = ChatFactory(assignment__offer__task__owner=user.profile)

        url = self.url
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = OrderedDict(
            {
                'id': chat.id,
                'created_at': mock.ANY,
                'offer': chat.assignment.offer.id,
                'service': chat.assignment.offer.task.service.id,
                'profile_name': chat.assignment.offer.helper.name,
            }
        )

        self.assertEqual(response.data[0], expected_data)

    def test_get_chats_doesnt_return_chats_from_other_users(self):
        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        ChatFactory()

        url = self.url
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_get_chats_respects_query_param_limit(self):
        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        ChatFactory(assignment__offer__helper=user.profile)
        ChatFactory(assignment__offer__helper=user.profile)

        url = self.url + '?limit=1'
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
