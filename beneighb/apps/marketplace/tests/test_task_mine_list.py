from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from apps.users.factories import UserWithProfileFactory

from apps.marketplace.factories import (
    OfferFactory,
    TaskFactory,
)
from apps.users.tests.utils import get_client_with_valid_token


class TaskMineListTestsCase(TestCase):
    url = '/marketplace/tasks/mine/'

    @classmethod
    def setUpTestData(cls):
        cls.USER = UserWithProfileFactory()
        cls.TASK_1 = TaskFactory(owner=cls.USER.profile)
        cls.TASK_2 = TaskFactory(owner=cls.USER.profile)

    def assert_helper_equal(self, response_helper, db_helper):
        self.assertEqual(response_helper['id'], db_helper.id)
        self.assertEqual(response_helper['name'], db_helper.name)
        self.assertEqual(
            response_helper['speaking_languages'], db_helper.speaking_languages
        )
        self.assertEqual(
            response_helper['services'], list(db_helper.services.all())
        )

    def test_returns_401_without_token(self):
        client = APIClient()

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_successful(self):
        client = get_client_with_valid_token(self.USER)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        task = response.data[0]
        self.assertEqual(task['service'], self.TASK_1.service_id)
        self.assertEqual(task['datetime_known'], self.TASK_1.datetime_known)
        self.assertEqual(
            task['datetime_options'], self.TASK_1.datetime_options
        )
        self.assertEqual(task['event_type'], self.TASK_1.event_type)
        self.assertEqual(task['address'], self.TASK_1.address)
        self.assertEqual(task['price_offer'], self.TASK_1.price_offer)
        self.assertEqual(task['offers'], [])

    def test_successful_inlcudes_all_offers(self):
        offer_1 = OfferFactory(task=self.TASK_1)
        offer_2 = OfferFactory(task=self.TASK_1)
        offer_3 = OfferFactory(task=self.TASK_2)

        client = get_client_with_valid_token(self.USER)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        task_1 = response.data[0]
        task_1_offers = task_1['offers']

        self.assertEqual(len(task_1_offers), 2)
        self.assertEqual(task_1_offers[0]['id'], offer_1.id)
        self.assertEqual(task_1_offers[0]['status'], offer_1.status)
        self.assertIsNotNone(task_1_offers[0]['created_at'])
        self.assert_helper_equal(task_1_offers[0]['helper'], offer_1.helper)

        self.assertEqual(task_1_offers[1]['id'], offer_2.id)
        self.assertEqual(task_1_offers[1]['status'], offer_2.status)
        self.assertIsNotNone(task_1_offers[1]['created_at'])
        self.assert_helper_equal(task_1_offers[1]['helper'], offer_2.helper)

        task_2 = response.data[1]
        task_2_offers = task_2['offers']

        self.assertEqual(len(task_2_offers), 1)
        self.assertEqual(task_2_offers[0]['id'], offer_3.id)
        self.assertEqual(task_2_offers[0]['status'], offer_3.status)
        self.assertIsNotNone(task_2_offers[0]['created_at'])
        self.assert_helper_equal(task_2_offers[0]['helper'], offer_3.helper)

    def test_no_tasks(self):
        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_shows_only_tasks_owned_by_user(self):
        user = UserWithProfileFactory()
        task = TaskFactory(owner=user.profile)
        client = get_client_with_valid_token(user)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], task.id)
        self.assertEqual(response.data[0]['owner'], user.profile.id)
