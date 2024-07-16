from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from apps.marketplace.factories import ServiceFactory
from apps.users.factories import UserWithProfileFactory
from apps.users.models import Block
from apps.users.tests.utils import get_client_with_valid_token

from rest_framework import status

from rest_framework.test import APIClient

from django.core.cache import cache
from django.test import TestCase

from firebase_admin._messaging_utils import (
    SenderIdMismatchError,
    UnregisteredError,
)
from requests.exceptions import HTTPError


class BlockUserGeneralTestCase(TestCase):
    url_template = '/users/profiles/{profile_id}/block/'

    @classmethod
    def setUpTestData(cls):
        cls.SERVICE = ServiceFactory()

    # TODO: Check if needed
    def setUp(self):
        pass

    def tearDown(self):
        cache.clear()
        super().tearDown()

    def test_block_user_unauthenticated_401(self):
        user_to_block = UserWithProfileFactory()

        client = APIClient()

        response = client.post(
            self.url_template.format(profile_id=user_to_block.profile.id)
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_block_user_succesful(self):
        user_to_block = UserWithProfileFactory()
        user_blocking = UserWithProfileFactory()
        client = get_client_with_valid_token(user_blocking)

        response = client.post(
            self.url_template.format(profile_id=user_to_block.profile.id)
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        block_qs = Block.objects.filter(
            blocker=user_to_block.profile, blocked=user_to_block.profile
        )

        self.assertTrue(block_qs.exists())
        self.assertEqual(block_qs.count(), 1)
