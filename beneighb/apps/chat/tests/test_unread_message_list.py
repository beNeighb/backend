from datetime import datetime
from unittest import mock
from collections import OrderedDict

from django.test import TestCase
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

from apps.chat.factories import ChatFactory, MessageFactory
from apps.users.factories import UserWithProfileFactory
from apps.users.tests.utils import get_client_with_valid_token


class UnreadMessageListTestCase(TestCase):
    url = '/chats/messages/?unread=true'

    @classmethod
    def setUpTestData(cls):
        cls.USER = UserWithProfileFactory()
        cls.CHAT = ChatFactory(assignment__offer__helper=cls.USER.profile)
        cls.TASK_OWNER = cls.CHAT.assignment.offer.task.owner

        # Hack: for some reason FatcoryBoy doesn't save profile for user
        cls.TASK_OWNER.user.save()

        cls.MESSAGE = MessageFactory(chat=cls.CHAT, sender=cls.TASK_OWNER)

    def test_returns_401_without_token(self):
        client = APIClient()

        response = client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_success_for_helper(self):
        client = get_client_with_valid_token(self.USER)
        response = client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        self.assertEqual(response.data[0]['id'], self.MESSAGE.id)

    def test_success_for_owner(self):
        offer_helper = self.CHAT.assignment.offer.helper

        expected_msg_ids = set()
        for i in range(3):
            msg = MessageFactory(chat=self.CHAT, sender=offer_helper)
            expected_msg_ids.add(msg.id)

        client = get_client_with_valid_token(self.TASK_OWNER.user)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 3)
        response_msg_ids = set([i['id'] for i in response.data])
        self.assertEqual(response_msg_ids, expected_msg_ids)

    def test_return_only_messages_for_my_chats(self):
        expected_msg = self.MESSAGE

        for i in range(3):
            MessageFactory()

        client = get_client_with_valid_token(self.USER)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], expected_msg.id)

    def test_return_messages_for_multiple_chats(self):
        expected_msg_ids = {self.MESSAGE.id}
        for i in range(3):
            chat = ChatFactory(assignment__offer__helper=self.USER.profile)
            msg = MessageFactory(
                chat=chat, sender=chat.assignment.offer.task.owner
            )
            expected_msg_ids.add(msg.id)

        client = get_client_with_valid_token(self.USER)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 4)

        response_msg_ids = set([i['id'] for i in response.data])
        self.assertEqual(response_msg_ids, expected_msg_ids)

    def test_doesnt_return_read_messages(self):
        user = UserWithProfileFactory()
        chat = ChatFactory(assignment__offer__helper=user.profile)
        task_owner = chat.assignment.offer.task.owner

        read_msg = MessageFactory(chat=chat, sender=task_owner)

        read_msg.read_at = datetime.now(tz=timezone.utc)
        read_msg.save()

        for i in range(3):
            MessageFactory(chat=chat, sender=task_owner)

        client = get_client_with_valid_token(user)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 3)

        response_msg_ids = set([i['id'] for i in response.data])
        self.assertNotIn(read_msg, response_msg_ids)

    def test_success_correct_fields_for_msg(self):
        client = get_client_with_valid_token(self.USER)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_msg = OrderedDict(
            {
                'id': self.MESSAGE.id,
                'chat': self.MESSAGE.chat.id,
                'sent_at': mock.ANY,
                'read_at': None,
                'is_mine': False,
                'text': self.MESSAGE.text,
            }
        )

        self.assertEqual(
            response.data[0],
            expected_msg,
        )

    def test_doesnt_work_without_unread_param(self):
        client = get_client_with_valid_token(self.USER)

        incorrect_url = '/chats/messages/'
        response = client.get(incorrect_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {'error': 'Invalid unread value. Must be "true"'}
        )

    def test_doesnt_work_with_incorrect_unread_param(self):
        client = get_client_with_valid_token(self.USER)

        incorrect_url = '/chats/messages/?unread=1'
        response = client.get(incorrect_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {'error': 'Invalid unread value. Must be "true"'}
        )
