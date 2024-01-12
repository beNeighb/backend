from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from apps.users.factories import (
    UserWithProfileFactory,
    UserWithVerifiedEmailFactory,
)
from apps.marketplace.factories import ServiceFactory
from apps.users.tests.utils import get_client_with_valid_token


class MyProfileViewTestCase(TestCase):
    url = '/users/profile/'

    def test_returns_401_without_token(self):
        client = APIClient()

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_not_exist(self):
        user_without_profile = UserWithVerifiedEmailFactory()

        client = get_client_with_valid_token(user_without_profile)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_profile_successful(self):
        service = ServiceFactory()
        EXPECTED_DATA = {
            'name': 'John Doe',
            'age_above_18': True,
            'agreed_with_conditions': True,
            'gender': 'female',
            'speaking_languages': ['eo', 'uk'],
            'services': [service.id],
        }

        user = UserWithProfileFactory(
            profile__name=EXPECTED_DATA['name'],
            profile__age_above_18=EXPECTED_DATA['age_above_18'],
            profile__agreed_with_conditions=EXPECTED_DATA[
                'agreed_with_conditions'
            ],
            profile__gender=EXPECTED_DATA['gender'],
            profile__speaking_languages=EXPECTED_DATA['speaking_languages'],
        )
        user.profile.services.add(service)
        user.profile.save()

        EXPECTED_DATA['id'] = user.profile.id

        client = get_client_with_valid_token(user)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, EXPECTED_DATA)
