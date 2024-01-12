from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from apps.users.factories import UserWithProfileFactory, ProfileFactory

from apps.marketplace.factories import (
    OfferFactory,
    ServiceFactory,
    TaskFactory,
)
from apps.users.tests.utils import get_client_with_valid_token


class TaskForMeListTestsCase(TestCase):
    url = '/marketplace/tasks/for-me/'

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

    def test_returns_401_without_token(self):
        client = APIClient()

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_tasks(self):
        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_show_applicable_tasks(self):
        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        service_1 = ServiceFactory(name='service_1')
        service_2 = ServiceFactory(name='service_2')
        service_3 = ServiceFactory(name='service_3')

        user.profile.services.add(service_1, service_2)
        user.profile.save()

        task_1 = TaskFactory(owner=ProfileFactory(), service=service_1)
        task_2 = TaskFactory(owner=ProfileFactory(), service=service_2)
        TaskFactory(owner=ProfileFactory(), service=service_3)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        tasks = {task_1.id: task_1, task_2.id: task_2}
        for result_task in response.data:
            task = tasks[result_task['id']]
            self.assertEqual(result_task['service'], task.service_id)
            self.assertIsNotNone(result_task['created_at'])
            self.assertEqual(
                result_task['datetime_known'], task.datetime_known
            )
            self.assertEqual(
                result_task['datetime_options'], task.datetime_options
            )
            self.assertEqual(result_task['event_type'], task.event_type)
            self.assertEqual(result_task['address'], task.address)
            self.assertEqual(result_task['price_offer'], task.price_offer)

    def test_doesnt_show_my_tasks(self):
        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        service_1 = ServiceFactory(name='service_1')
        user.profile.services.add(service_1)
        user.profile.save()

        task_1 = TaskFactory(owner=ProfileFactory(), service=service_1)
        my_task = TaskFactory(owner=user.profile, service=service_1)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], task_1.id)
        self.assertNotEqual(response.data[0]['id'], my_task.id)

    def test_show_my_offer_in_task(self):
        service_1 = ServiceFactory(name='service_1')
        user = UserWithProfileFactory()
        user.profile.services.add(service_1)
        user.profile.save()

        task_1 = TaskFactory(owner=ProfileFactory(), service=service_1)
        offer = OfferFactory(task=task_1, helper=user.profile)

        client = get_client_with_valid_token(user)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        offers = response.data[0]['offers']
        my_offer = offers[0]
        self.assertEqual(my_offer['id'], offer.id)
        self.assertEqual(my_offer['status'], offer.status)

        helper = my_offer['helper']
        self.assert_helper_equal(helper, user.profile)

    def test_doesnt_show_other_offers_in_task(self):
        service_1 = ServiceFactory(name='service_1')
        user = UserWithProfileFactory()
        user.profile.services.add(service_1)
        user.profile.save()

        task = TaskFactory(owner=ProfileFactory(), service=service_1)
        my_offer = OfferFactory(task=task, helper=user.profile)
        other_offer_1 = OfferFactory(task=task)  # noqa
        other_offer_2 = OfferFactory(task=task)  # noqa

        client = get_client_with_valid_token(user)

        response = client.get(self.url)
        offers = response.data[0]['offers']
        self.assertEqual(len(offers), 1)

        offer = offers[0]
        self.assertEqual(offer['id'], my_offer.id)
        self.assertEqual(offer['status'], my_offer.status)

        offer_helper = offer['helper']
        self.assert_helper_equal(offer_helper, user.profile)
