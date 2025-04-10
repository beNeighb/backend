from unittest import mock

from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from rest_framework.exceptions import ErrorDetail
from unittest import skip

from apps.users.factories import UserWithProfileFactory
from apps.marketplace.models import Offer, Task
from apps.marketplace.factories import TaskFactory
from apps.users.tests.utils import get_client_with_valid_token


class CreateOfferTestCase(TestCase):
    url = '/marketplace/offers/'

    @classmethod
    def setUpTestData(cls):
        cls.TASK = TaskFactory()
        cls.correct_data = {
            'task': cls.TASK.id,
        }

    def test_returns_401_without_token(self):
        client = APIClient()

        response = client.post(self.url, self.correct_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @mock.patch('apps.marketplace.views.offer.send_push_notification')
    def test_create_offer_successful(self, mocked_send_push_notification):
        user = UserWithProfileFactory()
        user.profile.services.add(self.TASK.service)
        client = get_client_with_valid_token(user)

        response = client.post(self.url, self.correct_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertIsNotNone(response.data['created_at'])
        self.assertEqual(Offer.objects.count(), 1)

        offer = Offer.objects.first()

        self.assertIsNotNone(offer.created_at)
        self.assertEqual(offer.task, self.TASK)
        self.assertEqual(offer.helper, user.profile)
        self.assertEqual(offer.status, 'pending')
        self.assertEqual(offer.chat.id, response.data['chat'])

        # Checking response correctness here, because we need offer.id
        expected_data_without_created_at = {
            'id': offer.id,
            'status': 'pending',
            'task': self.TASK.id,
            'helper': user.profile.id,
            'chat': offer.chat.id,
        }

        for key, val in expected_data_without_created_at.items():
            self.assertEqual(response.data[key], val)

    @mock.patch('apps.marketplace.views.offer.send_push_notification')
    def test_create_offer_notification(self, mocked_send_push_notification):
        user = UserWithProfileFactory()
        user.profile.services.add(self.TASK.service)
        client = get_client_with_valid_token(user)

        response = client.post(self.url, self.correct_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        offer = Offer.objects.first()

        self.assertEqual(mocked_send_push_notification.call_count, 1)
        self.assertEqual(
            mocked_send_push_notification.call_args[0][0],
            offer.task.owner,
        )
        self.assertEqual(
            mocked_send_push_notification.call_args[1]['data'],
            {
                'type': 'new_offer',
                'task_id': str(offer.task.id),
            },
        )

    def test_create_offer_with_incorrect_task_id(self):
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

    @mock.patch('apps.marketplace.views.offer.send_push_notification')
    def test_cannot_create_second_offer_for_task(
        self, _mocked_send_push_notification
    ):
        user = UserWithProfileFactory()
        user.profile.services.add(self.TASK.service)
        client = get_client_with_valid_token(user)

        response = client.post(self.url, self.correct_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Offer.objects.count(), 1)

        response = client.post(self.url, self.correct_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                'non_field_errors': [
                    ErrorDetail(
                        string='Only one offer is allowed per task.',
                        code='invalid',
                    )
                ]
            },
        )

    def test_cannot_create_offer_for_own_task(self):
        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        task = TaskFactory(owner=user.profile)

        data = {
            'task': task.id,
        }

        response = client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                'non_field_errors': [
                    ErrorDetail(
                        string='You can not offer to help your own task',
                        code='invalid',
                    )
                ]
            },
        )

    @skip
    def test_cannot_create_offer_for_helper_without_matching_service(self):
        user = UserWithProfileFactory()
        self.assertEqual(user.profile.services.count(), 0)

        client = get_client_with_valid_token(user)

        response = client.post(self.url, self.correct_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            response.data,
            {
                'non_field_errors': [
                    ErrorDetail(
                        string='You cannot create offer because you do not have a matching service.',  # noqa
                        code='invalid',
                    )
                ]
            },
        )

    def test_can_create_offer_for_helper_without_matching_service(self):
        user = UserWithProfileFactory()
        self.assertEqual(user.profile.services.count(), 0)

        client = get_client_with_valid_token(user)

        response = client.post(self.url, self.correct_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertIsNotNone(response.data['created_at'])
        self.assertEqual(Offer.objects.count(), 1)

        offer = Offer.objects.first()

        self.assertIsNotNone(offer.created_at)
        self.assertEqual(offer.task, self.TASK)
        self.assertEqual(offer.helper, user.profile)
        self.assertEqual(offer.status, 'pending')

        # Checking response correctness here, because we need offer.id
        expected_data_without_created_at = {
            'id': offer.id,
            'status': 'pending',
            'task': self.TASK.id,
            'helper': user.profile.id,
        }

        for key, val in expected_data_without_created_at.items():
            self.assertEqual(response.data[key], val)
