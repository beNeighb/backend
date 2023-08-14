from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import TestCase

from unittest.mock import patch, MagicMock
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()
AUTHORIZATION_HEADER_TEMPLATE = 'Bearer {token}'


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
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_can_authorize_with_correct_token(self):
        USERNAME = 'testuser'
        PASSWORD = '12345'
        User.objects.create_user(username=USERNAME, password=PASSWORD)

        client = APIClient()
        response = client.post(
            self.url, {'username': USERNAME, 'password': PASSWORD}
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

    def test_get_token_with_non_existing_user(self):
        client = APIClient()
        response = client.post(
            self.url,
            {'username': 'non_existant_user', 'password': 'incorrect_password'},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_token_with_incorrect_password(self):
        User.objects.create_user(username='testuser', password='12345')

        client = APIClient()
        response = client.post(
            self.url, {'username': 'testuser', 'password': 'incorrect_password'}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_token_successfull(self):
        USERNAME = 'testuser'
        PASSWORD = '12345'
        User.objects.create_user(username=USERNAME, password=PASSWORD)

        client = APIClient()
        response = client.post(
            self.url, {'username': USERNAME, 'password': PASSWORD}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)


class RefreshTokenTestCase(TestCase):
    url = '/auth/token/refresh/'

    def test_incorrect_refresh_token(self):
        client = APIClient()
        response = client.post(self.url, {'refresh': 'skdfjdskjf'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_correct_refresh_token(self):
        USERNAME = 'testuser'
        PASSWORD = '12345'
        User.objects.create_user(username=USERNAME, password=PASSWORD)

        client = APIClient()
        response = client.post(
            '/auth/token/', {'username': USERNAME, 'password': PASSWORD}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        refresh_token = response.data['refresh']
        response = client.post(self.url, {'refresh': refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_refreshes_refresh_token(self):
        USERNAME = 'testuser'
        PASSWORD = '12345'
        User.objects.create_user(username=USERNAME, password=PASSWORD)

        client = APIClient()
        response = client.post(
            '/auth/token/', {'username': USERNAME, 'password': PASSWORD}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        refresh_token = response.data['refresh']
        response = client.post(self.url, {'refresh': refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertNotEqual(refresh_token, response.data['refresh'])


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
        response = client.post(
            url, {'new_password1': NEW_PASSWORD, 'new_password2': NEW_PASSWORD}
        )

        expected_args = {
            'new_password1': [NEW_PASSWORD],
            'new_password2': [NEW_PASSWORD],
            'uid': [UIDB64],
            'token': [TOKEN],
        }

        mockec_called_request_data = mocked_post.call_args[0][0].data
        self.assertEquals(mockec_called_request_data, expected_args)
