from collections import OrderedDict
from django.test import TestCase
from unittest import mock

from rest_framework import status
from rest_framework.test import APIClient

from apps.users.factories import ProfileFactory, UserWithProfileFactory
from apps.marketplace.factories import (
    OfferFactory,
    ServiceFactory,
    TaskFactory,
)
from apps.marketplace.tests.utils import get_client_with_valid_token


class TaskWithMyOfferListTestsCase(TestCase):
    url = '/marketplace/tasks/with-my-offer/'

    def test_returns_401_without_token(self):
        client = APIClient()

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_offers(self):
        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_show_tasks_with_my_offer(self):
        service_1 = ServiceFactory(name='service_1')
        user = UserWithProfileFactory()
        user.profile.services.add(service_1)
        user.profile.save()

        task_1 = TaskFactory(owner=ProfileFactory(), service=service_1)
        task_2 = TaskFactory(service=service_1)
        task_3 = TaskFactory(service=service_1)

        my_offer_1 = OfferFactory(helper=user.profile, task=task_1)
        my_offer_2 = OfferFactory(helper=user.profile, task=task_2)
        another_offer_3 = OfferFactory(task=task_3)  # noqa

        client = get_client_with_valid_token(user)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        my_speaking_languages = user.profile.speaking_languages
        expected_my_offer_1 = {
            'id': my_offer_1.id,
            'status': my_offer_1.status,
            'created_at': mock.ANY,
            'helper': {
                'id': user.profile.id,
                'name': user.profile.name,
                'speaking_languages': my_speaking_languages,
                'services': [service_1.id],
            },
        }

        expected_my_offer_2 = {
            'id': my_offer_2.id,
            'status': my_offer_2.status,
            'created_at': mock.ANY,
            'helper': {
                'id': user.profile.id,
                'name': user.profile.name,
                'speaking_languages': my_speaking_languages,
                'services': [service_1.id],
            },
        }

        expected_task_1 = OrderedDict(
            {
                'id': task_1.id,
                'created_at': mock.ANY,
                'service': service_1.id,
                'owner': task_1.owner_id,
                'datetime_known': task_1.datetime_known,
                'datetime_options': task_1.datetime_options,
                'event_type': task_1.event_type,
                'address': task_1.address,
                'price_offer': task_1.price_offer,
                'offers': [expected_my_offer_1],
            }
        )
        expected_task_2 = OrderedDict(
            {
                'id': task_2.id,
                'created_at': mock.ANY,
                'service': service_1.id,
                'owner': task_2.owner_id,
                'datetime_known': task_2.datetime_known,
                'datetime_options': task_2.datetime_options,
                'event_type': task_2.event_type,
                'address': task_2.address,
                'price_offer': task_2.price_offer,
                'offers': [expected_my_offer_2],
            }
        )

        self.assertEqual(response.data[0], expected_task_1)
        self.assertEqual(response.data[1], expected_task_2)
