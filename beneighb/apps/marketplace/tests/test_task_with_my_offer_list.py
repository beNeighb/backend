from collections import OrderedDict
from django.test import TestCase
from unittest import mock

from rest_framework import status
from rest_framework.test import APIClient

from apps.users.factories import UserWithProfileFactory
from apps.marketplace.factories import (
    OfferFactory,
    ServiceFactory,
    TaskFactory,
)
from apps.users.tests.utils import get_client_with_valid_token


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
        service = ServiceFactory(name='service')
        user = UserWithProfileFactory()
        user.profile.services.add(service)
        user.profile.save()

        task_1 = TaskFactory(service=service)
        task_2 = TaskFactory(service=service)
        task_without_my_offer = TaskFactory(service=service)  # noqa

        my_offer_1 = OfferFactory(helper=user.profile, task=task_1)  # noqa
        my_offer_2 = OfferFactory(helper=user.profile, task=task_2)  # noqa

        client = get_client_with_valid_token(user)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        response_task_ids = [task['id'] for task in response.data]
        self.assertEqual(response_task_ids, [task_1.id, task_2.id])

    def test_returns_correct_fields(self):
        service = ServiceFactory(name='service')
        user = UserWithProfileFactory()
        user.profile.services.add(service)
        user.profile.save()

        task = TaskFactory(service=service)
        my_offer = OfferFactory(helper=user.profile, task=task)

        client = get_client_with_valid_token(user)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_my_offer = {
            'id': my_offer.id,
            'status': my_offer.status,
            'created_at': mock.ANY,
            'chat': my_offer.chat.id,
            'helper': {
                'id': user.profile.id,
                'name': user.profile.name,
                'speaking_languages': user.profile.speaking_languages,
                'services': [service.id],
                'city': user.profile.city,
            },
        }

        expected_task = OrderedDict(
            {
                'id': task.id,
                'created_at': mock.ANY,
                'service': service.id,
                'owner': task.owner_id,
                'datetime_known': task.datetime_known,
                'datetime_options': task.datetime_options,
                'event_type': task.event_type,
                'address': task.address,
                'price_offer': task.price_offer,
                'offers': [expected_my_offer],
                'info': task.info,
            }
        )

        self.assertEqual(response.data[0], expected_task)

    def test_doesnt_show_other_offers_in_task(self):
        service = ServiceFactory(name='service')
        user = UserWithProfileFactory()
        user.profile.services.add(service)
        user.profile.save()

        task = TaskFactory(service=service)

        my_offer_1 = OfferFactory(helper=user.profile, task=task)
        my_offer_2 = OfferFactory(helper=user.profile, task=task)
        another_offer = OfferFactory(task=task)  # noqa

        client = get_client_with_valid_token(user)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        offers_ids = [offer['id'] for offer in response.data[0]['offers']]

        self.assertIn(my_offer_1.id, offers_ids)
        self.assertIn(my_offer_2.id, offers_ids)

        self.assertNotIn(another_offer.id, offers_ids)
