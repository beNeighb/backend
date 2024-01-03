from unittest.mock import patch

from django.core import mail
from django.http import HttpResponse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.exceptions import ErrorDetail

from apps.users.factories import (
    UserWithUnVerifiedEmailFactory,
    UserWithVerifiedEmailFactory,
)
from apps.users.models import User, Profile

AUTHORIZATION_HEADER_TEMPLATE = 'Bearer {token}'

# Default user data
EMAIL = 'testuser@testuser.com'
PASSWORD = 'Abc12345_'
USERNAME = 'testuser'


class AuthorizationTestCase(TestCase):
    # TODO: Change to proper url
    AUTH_DUMMY_URL = '/auth/dummy/'
    url = '/auth/token/'

    def test_returns_401_without_token(self):
        # Include an appropriate `Authorization:` header on all requests.
        client = APIClient()

        AUTHORIZATION_HEADER = AUTHORIZATION_HEADER_TEMPLATE.format(
            token='invalid token'
        )
        client.credentials(HTTP_AUTHORIZATION=AUTHORIZATION_HEADER)

        urls = (self.AUTH_DUMMY_URL,)

        for url in urls:
            response = client.get(url)
            self.assertEqual(
                response.status_code, status.HTTP_401_UNAUTHORIZED
            )

    def test_can_authorize_with_correct_token(self):
        user_with_verified_email = UserWithVerifiedEmailFactory(
            username=USERNAME, email=EMAIL
        )
        user_with_verified_email.set_password(PASSWORD)
        user_with_verified_email.save()

        client = APIClient()
        response = client.post(
            self.url, {'username': EMAIL, 'password': PASSWORD}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data['access']

        client = APIClient()
        AUTHORIZATION_HEADER = AUTHORIZATION_HEADER_TEMPLATE.format(
            token=access_token
        )
        client.credentials(HTTP_AUTHORIZATION=AUTHORIZATION_HEADER)

        response = client.get(self.AUTH_DUMMY_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetTokenTestCase(TestCase):
    url = '/auth/token/'

    @classmethod
    def _build_verified_user_with_password(
        cls, username=USERNAME, email=EMAIL, password=PASSWORD
    ):
        user_with_verified_email = UserWithVerifiedEmailFactory(
            username=USERNAME, email=EMAIL
        )
        user_with_verified_email.set_password(PASSWORD)
        user_with_verified_email.save()

        return user_with_verified_email

    def test_get_token_with_non_existing_user(self):
        client = APIClient()
        response = client.post(
            self.url,
            {
                'username': 'non_existant_user',
                'password': 'incorrect_password',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_token_with_incorrect_password(self):
        self._build_verified_user_with_password()

        client = APIClient()
        response = client.post(
            self.url,
            {'username': 'testuser', 'password': 'incorrect_password'},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_token_with_non_verified_user(self):
        user_withot_unverified_email = UserWithUnVerifiedEmailFactory(
            username=USERNAME, email=EMAIL
        )
        user_withot_unverified_email.set_password(PASSWORD)
        user_withot_unverified_email.save()

        client = APIClient()
        response = client.post(
            self.url, {'username': EMAIL, 'password': PASSWORD}
        )

        expected_response = {
            'detail': ErrorDetail(
                string='Sorry, but you can only login with verified email',
                code='email_not_verified',
            )
        }

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(expected_response, response.data)

    def test_get_token_successfull(self):
        self._build_verified_user_with_password()

        client = APIClient()
        response = client.post(
            self.url, {'username': EMAIL, 'password': PASSWORD}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)


class RefreshTokenTestCase(TestCase):
    url = '/auth/token/refresh/'

    @classmethod
    def _build_verified_user_with_password(
        cls, username=USERNAME, email=EMAIL, password=PASSWORD
    ):
        user_with_verified_email = UserWithVerifiedEmailFactory(
            username=USERNAME, email=EMAIL
        )
        user_with_verified_email.set_password(PASSWORD)
        user_with_verified_email.save()

        return user_with_verified_email

    def test_incorrect_refresh_token(self):
        client = APIClient()
        response = client.post(self.url, {'refresh': 'skdfjdskjf'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_correct_refresh_token(self):
        self._build_verified_user_with_password(email=EMAIL, password=PASSWORD)

        client = APIClient()
        response = client.post(
            '/auth/token/', {'username': EMAIL, 'password': PASSWORD}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        refresh_token = response.data['refresh']
        response = client.post(self.url, {'refresh': refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_refreshes_refresh_token(self):
        self._build_verified_user_with_password(email=EMAIL, password=PASSWORD)

        client = APIClient()
        response = client.post(
            '/auth/token/', {'username': EMAIL, 'password': PASSWORD}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        refresh_token = response.data['refresh']
        response = client.post(self.url, {'refresh': refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertNotEqual(refresh_token, response.data['refresh'])


class RegistrationTestCase(TestCase):
    url = '/auth/registration/'

    def test_user_profile_is_not_created(self):
        data = {
            'email': 'test.user@email.com',
            'password1': PASSWORD,
            'password2': PASSWORD,
        }

        client = APIClient()
        response = client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Profile.objects.count(), 0)
        user = User.objects.get()
        self.assertEqual(user.profile, None)

    def test_correct_confirmation_email(self):
        data = {
            'email': 'test.user@email.com',
            'password1': PASSWORD,
            'password2': PASSWORD,
        }

        client = APIClient()
        response = client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        email = mail.outbox[0]
        expected_link = 'https://link.beneighb.com'

        self.assertIn(expected_link, email.body)
        self.assertIn('Please Confirm Your E-mail Address', email.subject)


@patch(
    'apps.auth0.views.PasswordResetConfirmView.post',
    return_value=HttpResponse(),
)
class BeneighbPasswordResetConfirmViewTestCase(TestCase):
    url_template = '/auth/password-reset-confirm/{uidb64}/{token}/'

    def test_view_is_called_with_uidb64_and_token(self, mocked_post):
        NEW_PASSWORD = 'New password 6 !'
        UIDB64 = 'Some uidb64'
        TOKEN = 'Some token'
        url = self.url_template.format(uidb64=UIDB64, token=TOKEN)

        client = APIClient()
        client.post(
            url, {'new_password1': NEW_PASSWORD, 'new_password2': NEW_PASSWORD}
        )

        expected_args = {
            'new_password1': [NEW_PASSWORD],
            'new_password2': [NEW_PASSWORD],
            'uid': [UIDB64],
            'token': [TOKEN],
        }

        mocked_called_request_data = mocked_post.call_args[0][0].data
        self.assertEqual(mocked_called_request_data, expected_args)


class ResetEmailSendsCorrectEmailTestCase(TestCase):
    url = '/auth/password-reset/'
    TEST_USER_EMAIL = 'test.user@email.com'
    data = {
        'email': TEST_USER_EMAIL,
    }

    def test_email_with_correct_link_is_sent(self):
        UserWithVerifiedEmailFactory(email=self.TEST_USER_EMAIL)

        client = APIClient()
        client.post(self.url, self.data)

        email = mail.outbox[0]
        expected_link = 'https://link.beneighb.com'

        self.assertIn(expected_link, email.body)
        self.assertIn('Your email is your username for login', email.body)
        self.assertIn('Password Reset E-mail', email.subject)
