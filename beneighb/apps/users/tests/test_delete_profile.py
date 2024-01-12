from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from apps.marketplace.models import Assignment

from apps.chat.factories import ChatFactory, MessageFactory
from apps.chat.models import Chat, Message

from apps.marketplace.models import Offer, Task

from apps.users.models import Profile, User
from apps.users.factories import UserWithProfileFactory
from apps.users.tests.utils import get_client_with_valid_token


class DeleteProfileTestCase(TestCase):
    url_template = '/users/profiles/{}/'

    def test_returns_401_without_token(self):
        client = APIClient()

        url = self.url_template.format(42)
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_profile_successful_for_helper(self):
        user = UserWithProfileFactory()
        profile = user.profile

        chat = ChatFactory(assignment__offer__helper=profile)
        message = MessageFactory(chat=chat, author=profile)
        message = MessageFactory(
            chat=chat, author=chat.assignment.offer.task.owner
        )
        assignment = chat.assignment
        offer = assignment.offer
        task = offer.task

        url = self.url_template.format(profile.id)

        client = get_client_with_valid_token(user)

        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(Profile.objects.filter(id=profile.id).count(), 0)
        self.assertEqual(User.objects.filter(id=profile.user.id).count(), 0)
        self.assertEqual(Chat.objects.filter(id=chat.id).count(), 0)
        self.assertEqual(Message.objects.filter(id=message.id).count(), 0)
        self.assertEqual(
            Assignment.objects.filter(id=assignment.id).count(), 0
        )
        self.assertEqual(Offer.objects.filter(id=offer.id).count(), 0)

        self.assertEqual(Task.objects.filter(id=task.id).count(), 1)

    def test_delete_profile_successful_for_owner(self):
        user = UserWithProfileFactory()
        profile = user.profile

        chat = ChatFactory(assignment__offer__task__owner=profile)
        message = MessageFactory(chat=chat, author=profile)
        message = MessageFactory(
            chat=chat, author=chat.assignment.offer.helper
        )
        assignment = chat.assignment
        offer = assignment.offer
        task = offer.task

        url = self.url_template.format(profile.id)

        client = get_client_with_valid_token(user)

        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(Profile.objects.filter(id=profile.id).count(), 0)
        self.assertEqual(User.objects.filter(id=profile.user.id).count(), 0)
        self.assertEqual(Chat.objects.filter(id=chat.id).count(), 0)
        self.assertEqual(Message.objects.filter(id=message.id).count(), 0)
        self.assertEqual(
            Assignment.objects.filter(id=assignment.id).count(), 0
        )
        self.assertEqual(Offer.objects.filter(id=offer.id).count(), 0)
        self.assertEqual(Task.objects.filter(id=task.id).count(), 0)

    def test_incorrect_profile_id(self):
        user = UserWithProfileFactory()
        profile = user.profile

        incorrect_profile_id = profile.id + 1
        url = self.url_template.format(incorrect_profile_id)

        self.assertEqual(
            Profile.objects.filter(id=incorrect_profile_id).count(), 0
        )

        client = get_client_with_valid_token(user)

        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(Profile.objects.filter(id=profile.id).count(), 1)

    def test_cannot_delete_another_user_profile(self):
        user = UserWithProfileFactory()
        profile = user.profile

        url = self.url_template.format(profile.id)

        another_user = UserWithProfileFactory()
        client = get_client_with_valid_token(another_user)

        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Profile.objects.filter(id=profile.id).count(), 1)
