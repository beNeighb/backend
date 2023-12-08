from django.test import TestCase
from unittest import mock

from rest_framework import status
from rest_framework.test import APIClient

from apps.users.factories import ProfileFactory, UserWithProfileFactory
from apps.marketplace.models import Task
from apps.marketplace.factories import (
    OfferFactory,
    ServiceFactory,
    TaskFactory,
)
from apps.marketplace.tests.utils import get_client_with_valid_token


class TaskWithMyOfferListTestsCase(TestCase):
    url = '/marketplace/tasks/with-my-offer/'

    def assert_helper_equal(self, response_helper, db_helper):
        self.assertEqual(response_helper['id'], db_helper.id)
        self.assertEqual(response_helper['name'], db_helper.name)
        self.assertEqual(
            response_helper['speaking_languages'], db_helper.speaking_languages
        )
        self.assertEqual(
            set(response_helper['services']),
            set(db_helper.services.values_list('id', flat=True)),
        )

    def assert_offer_equal(self, response_offer, db_offer):
        self.assertEqual(response_offer['id'], db_offer.id)
        self.assertEqual(response_offer['status'], db_offer.status)
        self.assert_helper_equal(response_offer['helper'], db_offer.helper)

    def assert_task_equal(self, response_task, db_task):
        self.assertEqual(response_task['id'], db_task.id)
        self.assertEqual(response_task['service'], db_task.service_id)
        self.assertEqual(
            response_task['datetime_known'], db_task.datetime_known
        )
        self.assertEqual(
            response_task['datetime_options'], db_task.datetime_options
        )
        self.assertEqual(response_task['event_type'], db_task.event_type)
        self.assertEqual(response_task['address'], db_task.address)
        self.assertEqual(response_task['price_offer'], db_task.price_offer)
        self.assert_offer_equal(
            response_task['offers'][0], db_task.offer_set.all()[0]
        )

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

        offer_1 = OfferFactory(helper=user.profile, task=task_1)
        offer_2 = OfferFactory(helper=user.profile, task=task_2)
        offer_3 = OfferFactory(task=task_3)

        client = get_client_with_valid_token(user)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        expected_data = [
            {
                'id': 1,
                'service': 1,
                'owner': 3,
                'datetime_known': True,
                'datetime_options': [],
                'event_type': 'online',
                'address': None,
                'price_offer': 100,
                'offers': [
                    {
                        'id': 1,
                        'status': 'pending',
                        'created_at': mock.ANY,
                        'helper': {
                            'id': 2,
                            'name': 'tmurray@example.net',
                            'speaking_languages': ['eo', 'uk'],
                            'services': [1],
                        },
                    },
                ],
            },
            {
                'id': 2,
                'service': 1,
                'owner': 4,
                'datetime_known': True,
                'datetime_options': [],
                'event_type': 'online',
                'address': None,
                'price_offer': 100,
                'offers': [
                    {
                        'id': 2,
                        'status': 'pending',
                        'created_at': mock.ANY,
                        'helper': {
                            'id': 2,
                            'name': 'tmurray@example.net',
                            'speaking_languages': ['eo', 'uk'],
                            'services': [1],
                        },
                    }
                ],
            },
        ]
