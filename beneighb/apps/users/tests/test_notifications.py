import requests

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from unittest import mock, skip
from unittest.mock import patch, Mock

from apps.marketplace.factories import ServiceFactory
from apps.marketplace.models import Service, Task
from apps.users.factories import UserWithProfileFactory
from apps.users.tests.utils import get_client_with_valid_token
from django.core.cache import cache
from django.test import TestCase
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient


class NotificationsTestCase(TestCase):
    url = '/marketplace/tasks/'

    @classmethod
    def setUpTestData(cls):
        cls.SERVICE = ServiceFactory()
        cls.correct_data = {
            'service': cls.SERVICE.id,
            'datetime_known': True,
            'datetime_options': [],
            'event_type': 'offline',
            'address': 'Some test address',
            'price_offer': 25,
        }

    def setUp(self):
        super().setUp()

        self.datetime_option = datetime.now(tz=timezone.utc) + timedelta(
            days=1
        )
        self.correct_data['datetime_options'] = [self.datetime_option]

    def send_notification(self):
        user = UserWithProfileFactory()

        client = get_client_with_valid_token(user)

        response = client.post(self.url, self.correct_data)

    def tearDown(self):
        cache.clear()
        super().tearDown()

    # @patch('requests.get')
    # @mock.patch('apps.users.notifications.send_push_notification')
    # def test_create_task_successful(self, mocked_send_push_notification, mocked_get):
    #     self.send_notification()

    #     self.assertEqual(mocked_send_push_notification.call_count, 1)

    @patch('apps.users.notifications.messaging.send')
    def test_send_push_notification_unregistered_error_erases_incorrect_fcm_tokens(
        self, mock_send
    ):
        from firebase_admin._messaging_utils import UnregisteredError

        mock_send.side_effect = UnregisteredError(
            'Device token is unregistered'
        )

        recipient = UserWithProfileFactory()
        recipient.profile.fcm_token = 'incorrect token'
        recipient.profile.save()

        user = UserWithProfileFactory()

        self.send_notification()

        self.assertEqual(user.profile.fcm_token, '')

    @patch('apps.users.notifications.messaging.send')
    def test_send_push_notification_httperror_erases_incorrect_fcm_tokens(
        self, mock_send
    ):
        from requests.exceptions import HTTPError

        mock_send.side_effect = HTTPError(
            '403 Client Error: Forbidden for url: https://fcm.googleapis.com/v1/projects/benehighb/messages:send'
        )

        recipient = UserWithProfileFactory()
        recipient.profile.fcm_token = 'incorrect token'
        recipient.profile.save()

        user = UserWithProfileFactory()

        self.send_notification()

        self.assertEqual(user.profile.fcm_token, '')


    @patch('apps.users.notifications.messaging.send')
    def test_send_push_notification_httperror_sender_id_mismatch_incorrect_fcm_tokens(
        self, mock_send
    ):
        from firebase_admin._messaging_utils import SenderIdMismatchError

        mock_send.side_effect = SenderIdMismatchError('SenderId mismatch')

        recipient = UserWithProfileFactory()
        recipient.profile.fcm_token = 'incorrect token'
        recipient.profile.save()

        user = UserWithProfileFactory()

        self.send_notification()

        self.assertEqual(user.profile.fcm_token, '')
