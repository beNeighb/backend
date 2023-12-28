from unittest import mock

from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from apps.users.factories import UserWithProfileFactory
from apps.marketplace.models import Offer
from apps.marketplace.factories import OfferFactory
from apps.marketplace.tests.utils import get_client_with_valid_token


class OfferMineListTestCase(TestCase):
    url = '/marketplace/offers/mine/'

    def test_returns_401_without_token(self):
        client = APIClient()

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_200_with_valid_token(self):
        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_returns_empty_list_when_no_offers(self):
        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        self.assertEqual(Offer.objects.count(), 0)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 0)

    def test_returns_only_my_offers(self):
        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        my_offer = OfferFactory(helper=user.profile)
        another_offer = OfferFactory()  # noqa

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], my_offer.id)

    def test_returns_offers_with_correct_data(self):
        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        offer = OfferFactory(helper=user.profile)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = {
            'id': offer.id,
            'status': 'pending',
            'created_at': mock.ANY,
            'task': offer.task.id,
            'helper': offer.helper.id,
            'is_accepted': False,
        }
        self.assertEqual(response.data[0], expected_data)
