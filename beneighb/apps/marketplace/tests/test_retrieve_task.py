from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from apps.users.factories import UserWithProfileFactory
from apps.marketplace.models import Task
from apps.marketplace.factories import TaskFactory
from apps.marketplace.tests.utils import get_client_with_valid_token


class RetrieveTaskTestCase(TestCase):
    url_template = '/marketplace/tasks/{}/'

    @classmethod
    def setUpTestData(cls):
        cls.USER = UserWithProfileFactory()
        cls.TASK = TaskFactory(owner=cls.USER.profile)
        cls.default_url = '/marketplace/tasks/{}/'.format(cls.TASK.id)

    def test_returns_401_without_token(self):
        client = APIClient()

        response = client.get(self.default_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_successful(self):
        client = get_client_with_valid_token(self.USER)

        response = client.get(self.default_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['service'], self.TASK.service_id)
        self.assertEqual(
            response.data['datetime_known'], self.TASK.datetime_known
        )
        self.assertEqual(
            response.data['datetime_options'], self.TASK.datetime_options
        )
        self.assertEqual(response.data['event_type'], self.TASK.event_type)
        self.assertEqual(response.data['address'], self.TASK.address)
        self.assertEqual(response.data['price_offer'], self.TASK.price_offer)

    def test_successful_by_another_user(self):
        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        response = client.get(self.default_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['service'], self.TASK.service_id)

    def test_non_existing_task_id(self):
        client = get_client_with_valid_token(self.USER)

        NON_EXISTING_TASK_ID = 1000
        self.assertEqual(
            Task.objects.filter(id=NON_EXISTING_TASK_ID).count(), 0
        )
        url = self.url_template.format(NON_EXISTING_TASK_ID)

        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
