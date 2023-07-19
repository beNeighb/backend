from django.test import TestCase
# from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


class AuthorizationTestCase(TestCase):
    # TODO: Change to proper url
    def test_returns_401_without_token(self):
        # Include an appropriate `Authorization:` header on all requests.
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token invalid token')

        urls = (
            '/auth/dummy/',
        )

        for url in urls:
            response = client.get(url)
            self.assertEqual(response.status_code, 401)
