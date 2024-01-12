from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from apps.users.factories import UserWithProfileFactory
from apps.marketplace.models import Offer, Task
from apps.marketplace.factories import OfferFactory, TaskFactory
from apps.users.tests.utils import get_client_with_valid_token


class RetrieveTaskTestCase(TestCase):
    url_template = '/marketplace/tasks/{}/'

    @classmethod
    def setUpTestData(cls):
        cls.USER = UserWithProfileFactory()
        cls.TASK = TaskFactory(owner=cls.USER.profile)
        cls.default_url = '/marketplace/tasks/{}/'.format(cls.TASK.id)

    def assert_offer_equal(self, response_offer, offer):
        self.assertEqual(response_offer['id'], offer.id)
        self.assertEqual(response_offer['status'], offer.status)
        self.assert_helper_equal(response_offer['helper'], offer.helper)

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

    def test_my_task_includes_all_offers(self):
        for i in range(3):
            OfferFactory(task=self.TASK)

        client = get_client_with_valid_token(self.USER)

        response = client.get(self.default_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        offers = response.data['offers']
        self.assertEqual(len(offers), 3)
        for response_offer in offers:
            offer = Offer.objects.get(id=response_offer['id'])
            self.assert_offer_equal(response_offer, offer)

    def test_another_user_task_includes_only_my_offer(self):
        user = UserWithProfileFactory()
        offer_1 = OfferFactory(task=self.TASK, helper=user.profile)
        for i in range(2):
            OfferFactory(task=self.TASK)

        client = get_client_with_valid_token(user)

        response = client.get(self.default_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        offers = response.data['offers']
        self.assertEqual(len(offers), 1)
        self.assert_offer_equal(offers[0], offer_1)
