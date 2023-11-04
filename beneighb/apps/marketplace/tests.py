from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.marketplace.models import Task
from apps.marketplace.factories import ServiceFactory
from apps.users.factories import UserWithVerifiedEmailFactory


AUTHORIZATION_HEADER_TEMPLATE = 'Bearer {token}'


class CreateTaskTestCase(TestCase):
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

    # TODO: Move to utils if used more than 2
    # TODO: Don't forget AUTHORIZATION_HEADER_TEMPLATE
    def _update_client_with_correct_token(self, user, client):
        refresh_token = RefreshToken.for_user(user)

        AUTHORIZATION_HEADER = AUTHORIZATION_HEADER_TEMPLATE.format(
            token=refresh_token.access_token
        )
        client.credentials(HTTP_AUTHORIZATION=AUTHORIZATION_HEADER)

    def test_returns_401_without_token(self):
        client = APIClient()

        response = client.post(self.url, self.correct_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_task_successful(self):
        user = UserWithVerifiedEmailFactory()

        client = APIClient()
        self._update_client_with_correct_token(user, client)

        response = client.post(self.url, self.correct_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Task.objects.count(), 1)

        task = Task.objects.get()

        self.assertIsNotNone(task.created_at)
        self.assertEqual(task.service, self.SERVICE)
        self.assertEqual(task.datetime_known, True)
        self.assertEqual(task.datetime_options, [])
        self.assertEqual(task.event_type, self.correct_data['event_type'])
        self.assertEqual(task.address, self.correct_data['address'])
        self.assertEqual(task.price_offer, self.correct_data['price_offer'])
