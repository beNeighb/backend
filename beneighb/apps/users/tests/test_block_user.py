from datetime import datetime, timedelta, timezone
from rest_framework.exceptions import ErrorDetail
from unittest.mock import patch

from apps.chat.factories import ChatFactory
from apps.chat.models import Chat
from apps.marketplace.factories import AssignmentFactory
from apps.marketplace.models import Assignment, Offer, Task
from apps.marketplace.factories import ServiceFactory, TaskFactory
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
            blocked_by=user_blocking.profile, blocked=user_to_block.profile
        )

        self.assertTrue(block_qs.exists())
        self.assertEqual(block_qs.count(), 1)

    def test_block_user_twice(self):
        user_to_block = UserWithProfileFactory()
        user_blocking = UserWithProfileFactory()

        client = get_client_with_valid_token(user_blocking)

        response = client.post(
            self.url_template.format(profile_id=user_to_block.profile.id)
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = client.post(
            self.url_template.format(profile_id=user_to_block.profile.id)
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        block_qs = Block.objects.filter(
            blocked_by=user_blocking.profile, blocked=user_to_block.profile
        )

        self.assertEqual(block_qs.count(), 1)

    def test_block_user_self(self):
        user_blocking = UserWithProfileFactory()

        client = get_client_with_valid_token(user_blocking)

        response = client.post(
            self.url_template.format(profile_id=user_blocking.profile.id)
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        block_qs = Block.objects.filter(blocked_by=user_blocking.profile)

        self.assertFalse(block_qs.exists())

    def test_block_user_not_found(self):
        user_blocking = UserWithProfileFactory()

        client = get_client_with_valid_token(user_blocking)

        response = client.post(self.url_template.format(profile_id=999))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        block_qs = Block.objects.filter(blocked_by=user_blocking.profile)

        self.assertFalse(block_qs.exists())


class BlockUserCorrespondingEntitiesDeletedTestCase(TestCase):
    url_template = '/users/profiles/{profile_id}/block/'

    @classmethod
    def setUpTestData(cls):
        cls.SERVICE = ServiceFactory()

    def tearDown(self):
        cache.clear()
        super().tearDown()

    def test_owner_blocks_helper(self):
        owner = UserWithProfileFactory()
        helper = UserWithProfileFactory()

        for i in range(2):
            chat = ChatFactory(
                offer__helper=helper.profile, offer__task__owner=owner.profile
            )
            AssignmentFactory(offer=chat.offer)

        self.assertEqual(Task.objects.count(), 2)
        self.assertEqual(Offer.objects.count(), 2)
        self.assertEqual(Assignment.objects.count(), 2)
        self.assertEqual(Chat.objects.count(), 2)

        client = get_client_with_valid_token(owner)

        response = client.post(
            self.url_template.format(profile_id=helper.profile.id)
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Tasks should not be deleted
        self.assertEqual(Task.objects.count(), 2)

        self.assertEqual(Offer.objects.count(), 0)
        self.assertEqual(Assignment.objects.count(), 0)
        self.assertEqual(Chat.objects.count(), 0)

    def test_helper_blocks_owner(self):
        owner = UserWithProfileFactory()
        helper = UserWithProfileFactory()

        for i in range(2):
            chat = ChatFactory(
                offer__helper=helper.profile, offer__task__owner=owner.profile
            )
            AssignmentFactory(offer=chat.offer)

        self.assertEqual(Task.objects.count(), 2)
        self.assertEqual(Offer.objects.count(), 2)
        self.assertEqual(Assignment.objects.count(), 2)
        self.assertEqual(Chat.objects.count(), 2)

        client = get_client_with_valid_token(helper)

        response = client.post(
            self.url_template.format(profile_id=owner.profile.id)
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Tasks should not be deleted
        self.assertEqual(Task.objects.count(), 2)

        self.assertEqual(Offer.objects.count(), 0)
        self.assertEqual(Assignment.objects.count(), 0)
        self.assertEqual(Chat.objects.count(), 0)

    def test_blocked_helper_cannot_create_offer(self):
        owner = UserWithProfileFactory()
        helper = UserWithProfileFactory()

        task = TaskFactory(owner=owner.profile)

        client = get_client_with_valid_token(owner)

        response = client.post(
            self.url_template.format(profile_id=helper.profile.id)
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Block.objects.count(), 1)

        client = get_client_with_valid_token(helper)

        response = client.post(
            '/marketplace/offers/',
            {
                'task': task.id,
                'status': 'pending',
            },
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(
            response.data,
            {
                'detail': ErrorDetail(
                    string='You are blocked by the task owner', code='error'
                )
            },
        )

    def test_owner_cannot_create_offer_to_blocked_profile(self):
        owner = UserWithProfileFactory()
        helper = UserWithProfileFactory()

        task_owner = TaskFactory(owner=owner.profile)
        chat = ChatFactory(
            offer__helper=helper.profile, offer__task__owner=owner.profile
        )

        task_helper = TaskFactory(owner=helper.profile)

        client = get_client_with_valid_token(owner)

        response = client.post(
            self.url_template.format(profile_id=helper.profile.id)
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Block.objects.count(), 1)
        self.assertEqual(Chat.objects.count(), 0)

        response = client.post(
            '/marketplace/offers/',
            {
                'task': task_helper.id,
                'status': 'pending',
            },
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(
            response.data,
            {
                'detail': ErrorDetail(
                    string='You are blocked by the task owner', code='error'
                )
            },
        )
