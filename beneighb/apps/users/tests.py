from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.exceptions import ErrorDetail

from apps.users.models import Profile, User
from apps.users.factories import (
    UserWithVerifiedEmailFactory,
)


AUTHORIZATION_HEADER_TEMPLATE = 'Bearer {token}'


class CreateProfileTestCase(TestCase):
    url_template = '/users/{0}/create-profile/'
    AUTH_DUMMY_URL = '/auth/dummy/'

    correct_data = {
        'name': 'Name',
        'age_above_18': True,
        'agreed_with_conditions': True,
        'gender': 'female',
        'speaking_languages': ['eo', 'uk'],
    }

    def _update_client_with_correct_token(self, user, client):
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh_token = RefreshToken.for_user(user)

        AUTHORIZATION_HEADER = AUTHORIZATION_HEADER_TEMPLATE.format(
            token=refresh_token.access_token
        )
        client.credentials(HTTP_AUTHORIZATION=AUTHORIZATION_HEADER)

    def test_returns_401_without_token(self):
        user = UserWithVerifiedEmailFactory()
        url = self.url_template.format(user.id)

        client = APIClient()

        response = client.post(url, self.correct_data)
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED
        )

    def test_create_profile_successful(self):
        user = UserWithVerifiedEmailFactory()
        url = self.url_template.format(user.id)

        client = APIClient()
        self._update_client_with_correct_token(user, client)

        response = client.post(url, self.correct_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(User.objects.count(), 1)

        user = User.objects.get()
        profile = user.profile

        self.assertEqual(type(profile), Profile)
        self.assertEqual(profile.name, 'Name')
        self.assertEqual(profile.age_above_18, True)
        self.assertEqual(profile.agreed_with_conditions, True)
        self.assertEqual(profile.gender, 'female')
        self.assertEqual(profile.speaking_languages, ['eo', 'uk'])

    def test_create_profile_for_user_with_profile(self):
        user = UserWithVerifiedEmailFactory()
        url = self.url_template.format(user.id)

        client = APIClient()
        self._update_client_with_correct_token(user, client)

        # Create profile first time
        response = client.post(url, self.correct_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(User.objects.count(), 1)

        user = User.objects.get()
        profile = user.profile
        self.assertEqual(type(profile), Profile)
        self.assertEqual(profile.name, 'Name')

        # Trying to create profile second time
        response = client.post(url, self.correct_data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_create_profile_without_any_data(self):
        data = {}

        user = UserWithVerifiedEmailFactory()
        url = self.url_template.format(user.id)

        client = APIClient()
        self._update_client_with_correct_token(user, client)

        response = client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                'name': [
                    ErrorDetail(
                        string='This field is required.', code='required'
                    )
                ],
                'age_above_18': [
                    ErrorDetail(
                        string='This field is required.', code='required'
                    )
                ],
                'agreed_with_conditions': [
                    ErrorDetail(
                        string='This field is required.', code='required'
                    )
                ],
                'gender': [
                    ErrorDetail(
                        string='This field is required.', code='required'
                    )
                ],
                'speaking_languages': [
                    ErrorDetail(
                        string='This field is required.', code='required'
                    )
                ],
            },
        )

    def test_create_profile_with_incorrect_gender(self):
        data = {
            'name': 'Name',
            'age_above_18': True,
            'agreed_with_conditions': True,
            'gender': 'female2',
            'speaking_languages': ['eo', 'uk'],
        }

        user = UserWithVerifiedEmailFactory()
        url = self.url_template.format(user.id)

        client = APIClient()
        self._update_client_with_correct_token(user, client)

        response = client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                'gender': [
                    ErrorDetail(
                        string='"female2" is not a valid choice.',
                        code='invalid_choice',
                    )
                ]
            },
        )

    def test_create_profile_with_incorrect_speaking_language(self):
        data = {
            'name': 'Name',
            'age_above_18': True,
            'agreed_with_conditions': True,
            'gender': 'female',
            'speaking_languages': ['eo2', 'uk'],
        }

        user = UserWithVerifiedEmailFactory()
        url = self.url_template.format(user.id)

        client = APIClient()
        self._update_client_with_correct_token(user, client)

        response = client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                'speaking_languages': {
                    0: [
                        ErrorDetail(
                            string='"eo2" is not a valid choice.',
                            code='invalid_choice',
                        )
                    ]
                }
            },
        )
