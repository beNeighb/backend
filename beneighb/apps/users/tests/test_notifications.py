from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from apps.marketplace.factories import ServiceFactory
from apps.users.factories import UserWithProfileFactory
from apps.users.tests.utils import get_client_with_valid_token

from django.core.cache import cache
from django.test import TestCase

from firebase_admin._messaging_utils import (
    SenderIdMismatchError,
    UnregisteredError,
)
from requests.exceptions import HTTPError


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

        return client.post(self.url, self.correct_data)

    def tearDown(self):
        cache.clear()
        super().tearDown()

    @patch('apps.users.notifications.messaging.send')
    def test_send_push_notification_unregistered_error_erases_fcm_tokens(
        self, mock_send
    ):
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
    def test_send_push_notification_httperror_erases_fcm_tokens(
        self, mock_send
    ):
        mock_send.side_effect = HTTPError(
            '403 Client Error: Forbidden for url: '
            'https://fcm.googleapis.com/v1/projects/benehighb/messages:send'
        )

        recipient = UserWithProfileFactory()
        recipient.profile.fcm_token = 'incorrect token'
        recipient.profile.save()

        user = UserWithProfileFactory()

        self.send_notification()

        self.assertEqual(user.profile.fcm_token, '')

    @patch('apps.users.notifications.messaging.send')
    def test_send_push_notification_httperror_sender_id_mismatch_fcm_tokens(
        self, mock_send
    ):
        mock_send.side_effect = SenderIdMismatchError('SenderId mismatch')

        recipient = UserWithProfileFactory()
        recipient.profile.fcm_token = 'incorrect token'
        recipient.profile.save()

        user = UserWithProfileFactory()

        self.send_notification()

        self.assertEqual(user.profile.fcm_token, '')
