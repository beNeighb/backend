from copy import deepcopy
from datetime import datetime, timedelta, timezone

from django.test import TestCase
from django.core.cache import cache

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.exceptions import ErrorDetail

from apps.users.factories import UserWithProfileFactory
from apps.marketplace.models import Offer, Service, Task
from apps.marketplace.factories import TaskFactory
from apps.marketplace.tests.utils import get_client_with_valid_token


class CreateOfferTestCase(TestCase):
    url = '/marketplace/offers/'

    @classmethod
    def setUpTestData(cls):
        cls.TASK = TaskFactory()
        cls.correct_data = {
            'task': cls.TASK.id,
            'status': 'pending',
        }

    # TODO: Change on response about idempotency
    # def tearDown(self):
    #     cache.clear()
    #     super().tearDown()

    def test_returns_401_without_token(self):
        client = APIClient()

        response = client.post(self.url, self.correct_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_task_successful(self):
        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        response = client.post(self.url, self.correct_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Offer.objects.count(), 1)

        offer = Offer.objects.get()

        self.assertIsNotNone(offer.created_at)
        self.assertEqual(offer.task, self.TASK)
        self.assertEqual(offer.helper, user.profile)
        self.assertEqual(offer.status, 'pending')

    def test_create_task_with_incorrect_task_id(self):
        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        NON_EXISTING_TASK_ID = Task.objects.last().id + 1000
        self.assertEqual(
            Task.objects.filter(id=NON_EXISTING_TASK_ID).count(), 0
        )

        data = {
            'status': 'pending',
            'task': NON_EXISTING_TASK_ID,
        }

        response = client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Offer.objects.count(), 0)

    def test_create_task_with_incorrect_status(self):
        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        data = {
            'status': 'incorrect status',
            'task': self.TASK.id,
        }

        response = client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Offer.objects.count(), 0)

    # def test_create_task_idempotent(self):
    #     user = UserWithProfileFactory()

    #     idempotency_key = 'Some idempotency key'
    #     client = get_client_with_valid_token(user)

    #     datetime_option = datetime.now(tz=timezone.utc) + timedelta(days=1)
    #     correct_data = deepcopy(self.correct_data)
    #     correct_data['datetime_options'] = [datetime_option]

    #     response = client.post(
    #         self.url, correct_data, HTTP_X_IDEMPOTENCY_KEY=idempotency_key
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #     self.assertEqual(Task.objects.count(), 1)

    #     response = client.post(
    #         self.url, correct_data, HTTP_X_IDEMPOTENCY_KEY=idempotency_key
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    #     self.assertEqual(Task.objects.count(), 1)
