from unittest import mock
from collections import OrderedDict

from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.exceptions import ErrorDetail

from apps.users.factories import UserWithProfileFactory
from apps.marketplace.models import Assignment, Chat, Offer
from apps.marketplace.factories import OfferFactory, TaskFactory
from apps.marketplace.tests.utils import get_client_with_valid_token


class AcceptOfferTestCase(TestCase):
    url_template = '/marketplace/offers/{}/accept/'

    def test_returns_401_without_token(self):
        client = APIClient()

        url = self.url_template.format(1)
        response = client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_accept_offer_successful(self):
        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        offer = OfferFactory(helper=user.profile)

        self.assertEqual(Assignment.objects.count(), 0)
        self.assertEqual(Chat.objects.count(), 0)

        url = self.url_template.format(offer.id)
        response = client.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        offer.refresh_from_db()
        self.assertEqual(offer.status, Offer.StatusTypes.ACCEPTED)

        self.assertEqual(Assignment.objects.count(), 1)
        assignment = Assignment.objects.first()
        self.assertEqual(assignment.offer, offer)
        self.assertEqual(assignment.status, Assignment.StatusTypes.PENDING)

        self.assertEqual(Chat.objects.count(), 1)
        chat = Chat.objects.first()
        self.assertEqual(chat.assignment, assignment)

        expected_data = {
            'offer': OrderedDict(
                {
                    'id': offer.id,
                    'task': offer.task.id,
                    'helper': offer.helper.id,
                    'status': 'accepted',
                    'created_at': mock.ANY,
                }
            ),
            'chat': OrderedDict(
                {
                    'id': chat.id,
                    'created_at': mock.ANY,
                    'offer': offer.id,
                    'service': offer.task.service.id,
                    'profile_name': user.profile.name,
                }
            ),
        }
        self.assertEqual(response.data['offer'], expected_data['offer'])
        self.assertEqual(response.data['chat'], expected_data['chat'])

    def test_cannot_accept_offer_of_another_user(self):
        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        another_user_offer = OfferFactory()

        url = self.url_template.format(another_user_offer.id)
        response = client.put(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            response.data,
            {
                'non_field_errors': [
                    ErrorDetail(
                        string="You cannot accept another users's offer",
                        code='invalid',
                    )
                ]
            },
        )

        self.assertEqual(Assignment.objects.count(), 0)
        self.assertEqual(Chat.objects.count(), 0)

    def test_accept_already_accepted_offer(self):
        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        offer = OfferFactory(
            helper=user.profile, status=Offer.StatusTypes.ACCEPTED
        )

        url = self.url_template.format(offer.id)
        response = client.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_offer = OrderedDict(
            {
                'id': offer.id,
                'task': offer.task.id,
                'helper': offer.helper.id,
                'status': 'accepted',
                'created_at': mock.ANY,
            }
        )
        expected_chat = OrderedDict(
            {
                'id': offer.assignment.chat.id,
                'created_at': mock.ANY,
                'offer': offer.id,
                'service': offer.task.service.id,
                'profile_name': user.profile.name,
            }
        )
        self.assertEqual(response.data['offer'], expected_offer)
        self.assertEqual(response.data['chat'], expected_chat)

    def test_accept_non_existing_offer(self):
        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        non_extisting_offer_id = 999
        self.assertEqual(
            Offer.objects.filter(id=non_extisting_offer_id).count(), 0
        )

        url = self.url_template.format(non_extisting_offer_id)
        response = client.put(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            response.data,
            {'detail': ErrorDetail(string='Not found.', code='not_found')},
        )

    def test_cannot_accept_offer_for_task_with_another_accepted_offer(self):
        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        task = TaskFactory()
        OfferFactory(task=task, status=Offer.StatusTypes.ACCEPTED)
        my_offer = OfferFactory(task=task, helper=user.profile)

        url = self.url_template.format(my_offer.id)
        response = client.put(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            response.data,
            {
                'status': [
                    ErrorDetail(
                        string='You cannot set status=accepted because there is already accepted offer for this task.',  # noqa
                        code='invalid',
                    )
                ]
            },
        )
