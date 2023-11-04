from copy import deepcopy

from django.test import TestCase
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework import status
from rest_framework.test import APIClient

from apps.users.factories import UserWithVerifiedEmailFactory
from apps.marketplace.models import Service, Task
from apps.marketplace.factories import ServiceFactory

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

    def get_client_with_valid_token(self, user):
        client = APIClient()
        self._update_client_with_correct_token(user, client)
        return client

    def test_returns_401_without_token(self):
        client = APIClient()

        response = client.post(self.url, self.correct_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_task_successful(self):
        user = UserWithVerifiedEmailFactory()

        client = self.get_client_with_valid_token(user)

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

    def test_create_task_with_incorrect_service_id(self):
        user = UserWithVerifiedEmailFactory()

        client = self.get_client_with_valid_token(user)

        incorrect_service_id = Service.objects.last().id + 1
        self.assertEqual(
            Service.objects.filter(id=incorrect_service_id).count(), 0
        )

        data_with_incorrect_service_id = deepcopy(self.correct_data)
        data_with_incorrect_service_id['service'] = incorrect_service_id

        response = client.post(self.url, data_with_incorrect_service_id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Task.objects.count(), 0)
