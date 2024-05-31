from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from apps.marketplace.factories import ServiceFactory

from apps.users.models import Profile
from apps.users.factories import UserWithProfileFactory
from apps.users.tests.utils import get_client_with_valid_token


class ProfileViewTestCase(TestCase):
    url_template = '/users/profiles/{}/'

    @classmethod
    def setUpTestData(cls):
        cls.USER = UserWithProfileFactory()
        cls.PROFILE = cls.USER.profile
        cls.url = cls.url_template.format(cls.PROFILE.id)

    def test_returns_401_without_token(self):
        client = APIClient()

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_not_exist(self):
        client = get_client_with_valid_token(self.USER)

        nonexisting_profile_id = self.PROFILE.id + 1
        self.assertEqual(
            Profile.objects.filter(id=nonexisting_profile_id).count(), 0
        )

        url = self.url_template.format(nonexisting_profile_id)
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_profile_successful(self):
        user = UserWithProfileFactory()
        profile = user.profile

        service = ServiceFactory()
        profile.services.add(service)
        profile.save()

        EXPECTED_DATA = {
            'id': profile.id,
            'name': profile.name,
            'speaking_languages': profile.speaking_languages,
            'services': [service.id],
            'city': profile.city,
        }

        client = get_client_with_valid_token(self.USER)

        url = self.url_template.format(user.profile.id)

        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, EXPECTED_DATA)
