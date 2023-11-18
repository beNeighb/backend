from copy import deepcopy
from datetime import datetime, timedelta, timezone

from django.test import TestCase
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.exceptions import ErrorDetail

from apps.users.factories import (
    UserWithVerifiedEmailFactory,
    UserWithProfileFactory,
)
from apps.marketplace.models import Service, Task
from apps.marketplace.factories import ServiceFactory, TaskFactory


# TODO: Move to utils
def update_client_with_correct_token(user, client):
    AUTHORIZATION_HEADER_TEMPLATE = 'Bearer {token}'
    refresh_token = RefreshToken.for_user(user)

    AUTHORIZATION_HEADER = AUTHORIZATION_HEADER_TEMPLATE.format(
        token=refresh_token.access_token
    )
    client.credentials(HTTP_AUTHORIZATION=AUTHORIZATION_HEADER)


def get_client_with_valid_token(user):
    client = APIClient()
    update_client_with_correct_token(user, client)
    return client


class CreateTaskTestCase(TestCase):
    url = '/marketplace/tasks/'

    @classmethod
    def setUpTestData(cls):
        cls.SERVICE = ServiceFactory()
        cls.correct_data = {
            'service': cls.SERVICE.id,
            'datetime_known': True,
            'datetime_options': [],
            'event_type': 'offline',
            'address': 'Some test address',
            'price_offer': 25,
        }

    def tearDown(self):
        cache.clear()
        super().tearDown()

    def test_returns_401_without_token(self):
        client = APIClient()

        response = client.post(self.url, self.correct_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_task_successful(self):
        user = UserWithVerifiedEmailFactory()

        client = get_client_with_valid_token(user)

        datetime_option = datetime.now(tz=timezone.utc) + timedelta(days=1)
        correct_data = deepcopy(self.correct_data)
        correct_data['datetime_options'] = [datetime_option]

        response = client.post(self.url, correct_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Task.objects.count(), 1)

        task = Task.objects.get()

        self.assertIsNotNone(task.created_at)
        self.assertEqual(task.service, self.SERVICE)
        self.assertEqual(task.datetime_known, True)
        self.assertEqual(task.datetime_options, [datetime_option])
        self.assertEqual(task.event_type, self.correct_data['event_type'])
        self.assertEqual(task.address, self.correct_data['address'])
        self.assertEqual(task.price_offer, self.correct_data['price_offer'])

    def test_create_task_idempotent(self):
        user = UserWithVerifiedEmailFactory()

        idempotency_key = 'Some idempotency key'
        client = get_client_with_valid_token(user)

        datetime_option = datetime.now(tz=timezone.utc) + timedelta(days=1)
        correct_data = deepcopy(self.correct_data)
        correct_data['datetime_options'] = [datetime_option]

        response = client.post(
            self.url, correct_data, HTTP_X_IDEMPOTENCY_KEY=idempotency_key
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Task.objects.count(), 1)

        response = client.post(
            self.url, correct_data, HTTP_X_IDEMPOTENCY_KEY=idempotency_key
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(Task.objects.count(), 1)

    def test_create_task_without_service_id(self):
        user = UserWithVerifiedEmailFactory()

        client = get_client_with_valid_token(user)

        data_without_service_id = deepcopy(self.correct_data)
        del data_without_service_id['service']

        response = client.post(self.url, data_without_service_id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(
            response.data,
            {
                'service': [
                    ErrorDetail(
                        string='This field is required.', code='required'
                    )
                ]
            },
        )

    def test_create_task_with_incorrect_service_id(self):
        user = UserWithVerifiedEmailFactory()

        client = get_client_with_valid_token(user)

        incorrect_service_id = Service.objects.last().id + 1
        self.assertEqual(
            Service.objects.filter(id=incorrect_service_id).count(), 0
        )

        data_with_incorrect_service_id = deepcopy(self.correct_data)
        data_with_incorrect_service_id['service'] = incorrect_service_id

        response = client.post(self.url, data_with_incorrect_service_id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(
            response.data,
            {
                'service': [
                    ErrorDetail(
                        string=(
                            f'Invalid pk "{incorrect_service_id}"'
                            ' - object does not exist.'
                        ),
                        code='does_not_exist',
                    )
                ]
            },
        )


class CreateTaskPriceOfferTestCase(TestCase):
    url = '/marketplace/tasks/'

    @classmethod
    def setUpTestData(cls):
        cls.SERVICE = ServiceFactory()
        cls.data = {
            'service': cls.SERVICE.id,
            'datetime_known': False,
            'event_type': 'online',
        }

    def test_create_task_without_price_offer(self):
        user = UserWithVerifiedEmailFactory()

        client = get_client_with_valid_token(user)

        response = client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(
            response.data,
            {
                'price_offer': [
                    ErrorDetail(
                        string='This field is required.', code='required'
                    )
                ]
            },
        )

    def test_create_task_with_negative_price_offer(self):
        user = UserWithVerifiedEmailFactory()

        client = get_client_with_valid_token(user)

        data = deepcopy(self.data)
        data['price_offer'] = -1

        response = client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(
            response.data,
            {
                'price_offer': [
                    ErrorDetail(
                        string='price_offer should be greater than 0',
                        code='invalid',
                    )
                ]
            },
        )

    def test_create_task_with_zero_price_offer(self):
        user = UserWithVerifiedEmailFactory()

        client = get_client_with_valid_token(user)

        data = deepcopy(self.data)
        data['price_offer'] = 0

        response = client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(
            response.data,
            {
                'price_offer': [
                    ErrorDetail(
                        string='price_offer should be greater than 0',
                        code='invalid',
                    )
                ]
            },
        )

    def test_create_task_with_price_offer_not_int(self):
        user = UserWithVerifiedEmailFactory()

        client = get_client_with_valid_token(user)

        data = deepcopy(self.data)
        data['price_offer'] = 'abc'

        response = client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(
            response.data,
            {
                'price_offer': [
                    ErrorDetail(
                        string='A valid integer is required.', code='invalid'
                    )
                ]
            },
        )


class CreateTaskEventTypeTestCase(TestCase):
    url = '/marketplace/tasks/'

    @classmethod
    def setUpTestData(cls):
        cls.SERVICE = ServiceFactory()
        cls.data = {
            'service': cls.SERVICE.id,
            'datetime_known': False,
            'datetime_options': [],
            'event_type': 'offline',
            'address': 'Some test address',
            'price_offer': 25,
        }

    def test_create_task_without_event_type(self):
        user = UserWithVerifiedEmailFactory()

        client = get_client_with_valid_token(user)

        data = deepcopy(self.data)
        del data['event_type']

        response = client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(
            response.data,
            {
                'event_type': [
                    ErrorDetail(
                        string='This field is required.', code='required'
                    )
                ]
            },
        )

    def test_create_task_with_incorrect_event_type(self):
        user = UserWithVerifiedEmailFactory()

        client = get_client_with_valid_token(user)

        data = deepcopy(self.data)
        data['event_type'] = 'Incorrect event_type'

        response = client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(
            response.data,
            {
                'event_type': [
                    ErrorDetail(
                        string='"Incorrect event_type" is not a valid choice.',
                        code='invalid_choice',
                    )
                ]
            },
        )

    def test_create_task_with_event_type_online_and_address(self):
        user = UserWithVerifiedEmailFactory()

        client = get_client_with_valid_token(user)

        data = deepcopy(self.data)
        data['event_type'] = 'online'
        data['address'] = 'Some test address'

        response = client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(
            response.data,
            {
                'address': [
                    ErrorDetail(
                        string=(
                            "For event_type=online "
                            "address shouldn't be present"
                        ),
                        code='invalid',
                    )
                ]
            },
        )

    def test_create_task_with_event_type_offline_without_address(self):
        user = UserWithVerifiedEmailFactory()

        client = get_client_with_valid_token(user)

        data = deepcopy(self.data)
        data['event_type'] = 'offline'
        del data['address']

        response = client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(
            response.data,
            {
                'address': [
                    ErrorDetail(
                        string='For event_type=offline address is required',
                        code='invalid',
                    )
                ]
            },
        )

    def test_create_task_with_event_type_offline_with_empty_address(self):
        user = UserWithVerifiedEmailFactory()

        client = get_client_with_valid_token(user)

        data = deepcopy(self.data)
        data['event_type'] = 'offline'
        data['address'] = ''

        response = client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(
            response.data,
            {
                'address': [
                    ErrorDetail(
                        string='For event_type=offline address is required',
                        code='invalid',
                    )
                ]
            },
        )


class CreateTaskDatetimeKnownTestCase(TestCase):
    url = '/marketplace/tasks/'

    @classmethod
    def setUpTestData(cls):
        cls.SERVICE = ServiceFactory()
        cls.data = {
            'service': cls.SERVICE.id,
            'datetime_known': True,
            'datetime_options': [],
            'event_type': 'offline',
            'address': 'Some test address',
            'price_offer': 25,
        }

    def test_create_task_without_datetime_known(self):
        user = UserWithVerifiedEmailFactory()

        client = get_client_with_valid_token(user)

        data_without_datetime_known = deepcopy(self.data)
        del data_without_datetime_known['datetime_known']

        response = client.post(self.url, data_without_datetime_known)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Task.objects.count(), 0)

    def test_create_task_successful(self):
        user = UserWithVerifiedEmailFactory()

        client = get_client_with_valid_token(user)

        datetime_option = datetime.now(tz=timezone.utc) + timedelta(days=1)
        data = deepcopy(self.data)
        data['datetime_options'] = [datetime_option]

        response = client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Task.objects.count(), 1)
        task = Task.objects.first()
        self.assertEqual(task.datetime_options, data['datetime_options'])

    def test_create_task_datetime_unknown_and_options_present(self):
        user = UserWithVerifiedEmailFactory()

        client = get_client_with_valid_token(user)

        datetime_option = datetime.now(tz=timezone.utc) + timedelta(days=1)
        data = deepcopy(self.data)
        data['datetime_known'] = False
        data['datetime_options'] = [datetime_option]

        response = client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(
            response.data,
            {
                'datetime_options': [
                    'For datetime_known=False datetime_options should be empty'
                ]
            },
        )

    def test_create_task_without_required_datetime_options(self):
        user = UserWithVerifiedEmailFactory()
        client = get_client_with_valid_token(user)

        response = client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(
            response.data,
            {
                'datetime_options': [
                    'datetime_options is required when date_timeknow is True'
                ]
            },
        )

    def test_create_task_with_incorrect_format_required_datetime_options(self):
        user = UserWithVerifiedEmailFactory()
        client = get_client_with_valid_token(user)

        data = deepcopy(self.data)
        data['datetime_options'] = [1]

        response = client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(
            response.data,
            {
                'datetime_options': {
                    0: [
                        ErrorDetail(
                            string=(
                                'Datetime has wrong format. '
                                'Use one of these formats instead: '
                                'YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z].'  # noqa
                            ),
                            code='invalid',
                        )
                    ]
                }
            },
        )

    def test_create_task_with_datetime_option_in_the_past(self):
        user = UserWithVerifiedEmailFactory()
        client = get_client_with_valid_token(user)

        datetime_option_1 = datetime.now(tz=timezone.utc) + timedelta(days=1)
        datetime_option_2 = datetime.now(tz=timezone.utc) + timedelta(days=-1)
        datetime_option_3 = datetime.now(tz=timezone.utc) + timedelta(days=1)

        data = deepcopy(self.data)
        data['datetime_options'] = [
            datetime_option_1,
            datetime_option_2,
            datetime_option_3,
        ]

        response = client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(
            response.data,
            {
                'datetime_options': [
                    ErrorDetail(
                        string='All datetime_options should be in the future',
                        code='invalid',
                    )
                ]
            },
        )

    def test_create_task_with_more_than_3_datetime_options(self):
        user = UserWithVerifiedEmailFactory()
        client = get_client_with_valid_token(user)

        data = deepcopy(self.data)
        data['datetime_options'] = [
            datetime.now(tz=timezone.utc) + timedelta(days=1) for i in range(4)
        ]

        response = client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(
            response.data,
            {
                'datetime_options': [
                    ErrorDetail(
                        string=(
                            'List contains 4 items, '
                            'it should contain no more than 3.'
                        ),
                        code='max_length',
                    )
                ]
            },
        )


class RetrieveTaskTestCase(TestCase):
    url_template = '/marketplace/tasks/{}/'

    @classmethod
    def setUpTestData(cls):
        cls.USER = UserWithVerifiedEmailFactory()
        cls.TASK = TaskFactory(owner=cls.USER)
        cls.default_url = '/marketplace/tasks/{}/'.format(cls.TASK.id)

    def test_returns_401_without_token(self):
        client = APIClient()

        response = client.get(self.default_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_successful(self):
        client = get_client_with_valid_token(self.USER)

        response = client.get(self.default_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['service'], self.TASK.service_id)
        self.assertEqual(
            response.data['datetime_known'], self.TASK.datetime_known
        )
        self.assertEqual(
            response.data['datetime_options'], self.TASK.datetime_options
        )
        self.assertEqual(response.data['event_type'], self.TASK.event_type)
        self.assertEqual(response.data['address'], self.TASK.address)
        self.assertEqual(response.data['price_offer'], self.TASK.price_offer)

    def test_successful_by_another_user(self):
        user = UserWithVerifiedEmailFactory()
        client = get_client_with_valid_token(user)

        response = client.get(self.default_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['service'], self.TASK.service_id)

    def test_non_existing_task_id(self):
        client = get_client_with_valid_token(self.USER)

        NON_EXISTING_TASK_ID = 1000
        self.assertEqual(
            Task.objects.filter(id=NON_EXISTING_TASK_ID).count(), 0
        )
        url = self.url_template.format(NON_EXISTING_TASK_ID)

        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ListMineTasksTestsCase(TestCase):
    url = '/marketplace/tasks/mine/'

    @classmethod
    def setUpTestData(cls):
        cls.USER = UserWithVerifiedEmailFactory()
        cls.TASK_1 = TaskFactory(owner=cls.USER)
        cls.TASK_2 = TaskFactory(owner=cls.USER)
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
        user = UserWithVerifiedEmailFactory()
        client = get_client_with_valid_token(user)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_shows_only_tasks_owned_by_user(self):
        user = UserWithVerifiedEmailFactory()
        task = TaskFactory(owner=user)
        client = get_client_with_valid_token(user)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], task.id)
        self.assertEqual(response.data[0]['owner'], user.id)


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

        task_1 = TaskFactory(
            owner=UserWithVerifiedEmailFactory(), service=service_1
        )
        task_2 = TaskFactory(
            owner=UserWithVerifiedEmailFactory(), service=service_2
        )
        TaskFactory(owner=UserWithVerifiedEmailFactory(), service=service_3)

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
