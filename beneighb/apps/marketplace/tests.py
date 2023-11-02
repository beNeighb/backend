from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient


class CreateTaskTestCase(TestCase):
    url = '/marketplace/tasks/'

    correct_data = {
    }

    def test_returns_401_without_token(self):
        client = APIClient()

        response = client.post(self.url, self.correct_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
