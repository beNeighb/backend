# from copy import deepcopy
# from datetime import datetime, timedelta, timezone

from django.test import TestCase

# from django.core.cache import cache

from rest_framework import status
from rest_framework.test import APIClient

# from rest_framework.exceptions import ErrorDetail

from apps.users.factories import UserWithProfileFactory, ProfileFactory

# from apps.marketplace.models import Service, Task
from apps.marketplace.factories import ServiceFactory, TaskFactory
from apps.marketplace.tests.utils import get_client_with_valid_token


class ListMineTasksTestsCase(TestCase):
    url = '/marketplace/tasks/mine/'

    @classmethod
    def setUpTestData(cls):
        cls.USER = UserWithProfileFactory()
        cls.TASK_1 = TaskFactory(owner=cls.USER.profile)
        cls.TASK_2 = TaskFactory(owner=cls.USER.profile)
        cls.TASKS = [cls.TASK_1, cls.TASK_2]

    def test_returns_401_without_token(self):
        client = APIClient()

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_successful(self):
        client = get_client_with_valid_token(self.USER)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        task = response.data[0]
        self.assertEqual(task['service'], self.TASK_1.service_id)
        self.assertEqual(task['datetime_known'], self.TASK_1.datetime_known)
        self.assertEqual(
            task['datetime_options'], self.TASK_1.datetime_options
        )
        self.assertEqual(task['event_type'], self.TASK_1.event_type)
        self.assertEqual(task['address'], self.TASK_1.address)
        self.assertEqual(task['price_offer'], self.TASK_1.price_offer)

    def test_no_tasks(self):
        user = UserWithProfileFactory()
        client = get_client_with_valid_token(user)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_shows_only_tasks_owned_by_user(self):
        user = UserWithProfileFactory()
        task = TaskFactory(owner=user.profile)
        client = get_client_with_valid_token(user)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], task.id)
        self.assertEqual(response.data[0]['owner'], user.profile.id)


class ListForMeTasksTestsCase(TestCase):
    url = '/marketplace/tasks/for-me/'

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
        service_2 = ServiceFactory(name='service_1')
        service_3 = ServiceFactory(name='service_1')

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
            self.assertEqual(
                result_task['datetime_known'], task.datetime_known
            )
            self.assertEqual(
                result_task['datetime_options'], task.datetime_options
            )
            self.assertEqual(result_task['event_type'], task.event_type)
            self.assertEqual(result_task['address'], task.address)
            self.assertEqual(result_task['price_offer'], task.price_offer)
