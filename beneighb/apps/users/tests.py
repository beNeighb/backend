from copy import deepcopy
from django.test import TestCase
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.exceptions import ErrorDetail

from apps.marketplace.factories import ServiceFactory
from apps.marketplace.models import Service

from apps.users.models import Profile, User
from apps.users.factories import (
    UserWithProfileFactory,
    UserWithVerifiedEmailFactory,
)

AUTHORIZATION_HEADER_TEMPLATE = 'Bearer {token}'


class CreateProfileTestCase(TestCase):
    url = '/users/create-profile/'

    correct_data = {
        'name': 'Name',
        'age_above_18': True,
        'agreed_with_conditions': True,
        'gender': 'female',
        'speaking_languages': ['eo', 'uk'],
        'subcategories': [],
    }

    list_of_all_languages = [
        'af',
        'ar',
        'hy',
        'bn',
        'bg',
        'zh',
        'hr',
        'cs',
        'da',
        'nl',
        'en',
        'et',
        'fa',
        'fi',
        'fr',
        'ka',
        'de',
        'el',
        'hi',
        'hu',
        'id',
        'it',
        'ja',
        'kk',
        'ko',
        'ku',
        'mk',
        'no',
        'pl',
        'pt',
        'ro',
        'ru',
        'sk',
        'sl',
        'es',
        'sv',
        'th',
        'tr',
        'uk',
        'ur',
        'uz',
        'vi',
    ]

    def _update_client_with_correct_token(self, user, client):
        refresh_token = RefreshToken.for_user(user)

        AUTHORIZATION_HEADER = AUTHORIZATION_HEADER_TEMPLATE.format(
            token=refresh_token.access_token
        )
        client.credentials(HTTP_AUTHORIZATION=AUTHORIZATION_HEADER)

    def test_returns_401_without_token(self):
        client = APIClient()

        response = client.post(self.url, self.correct_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_profile_successful(self):
        user = UserWithVerifiedEmailFactory()

        client = APIClient()
        self._update_client_with_correct_token(user, client)

        response = client.post(self.url, self.correct_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(User.objects.count(), 1)

        user = User.objects.get()
        profile = user.profile

        self.assertEqual(type(profile), Profile)
        self.assertEqual(profile.name, 'Name')
        self.assertEqual(profile.age_above_18, True)
        self.assertEqual(profile.agreed_with_conditions, True)
        self.assertEqual(profile.gender, 'female')
        self.assertEqual(profile.speaking_languages, ['eo', 'uk'])

    def test_create_profile_successful_with_all_languages(self):
        user = UserWithVerifiedEmailFactory()

        client = APIClient()
        self._update_client_with_correct_token(user, client)

        correct_data_with_all_languages = deepcopy(self.correct_data)
        correct_data_with_all_languages[
            'speaking_languages'
        ] = self.list_of_all_languages

        response = client.post(self.url, correct_data_with_all_languages)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(User.objects.count(), 1)

        user = User.objects.get()
        profile = user.profile

        self.assertEqual(
            profile.speaking_languages, self.list_of_all_languages
        )

    def test_create_profile_for_user_with_profile(self):
        user = UserWithVerifiedEmailFactory()

        client = APIClient()
        self._update_client_with_correct_token(user, client)

        # Create profile first time
        response = client.post(self.url, self.correct_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(User.objects.count(), 1)

        user = User.objects.get()
        profile = user.profile
        self.assertEqual(type(profile), Profile)
        self.assertEqual(profile.name, 'Name')

        # Trying to create profile second time
        response = client.post(self.url, self.correct_data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_create_profile_without_any_data(self):
        data = {}

        user = UserWithVerifiedEmailFactory()

        client = APIClient()
        self._update_client_with_correct_token(user, client)

        response = client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                'name': [
                    ErrorDetail(
                        string='This field is required.', code='required'
                    )
                ],
                'age_above_18': [
                    ErrorDetail(
                        string='This field is required.', code='required'
                    )
                ],
                'agreed_with_conditions': [
                    ErrorDetail(
                        string='This field is required.', code='required'
                    )
                ],
                'gender': [
                    ErrorDetail(
                        string='This field is required.', code='required'
                    )
                ],
                'speaking_languages': [
                    ErrorDetail(
                        string='This field is required.', code='required'
                    )
                ],
            },
        )

    def test_create_profile_with_incorrect_gender(self):
        data = deepcopy(self.correct_data)
        data['gender'] = 'female2'

        user = UserWithVerifiedEmailFactory()

        client = APIClient()
        self._update_client_with_correct_token(user, client)

        response = client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                'gender': [
                    ErrorDetail(
                        string='"female2" is not a valid choice.',
                        code='invalid_choice',
                    )
                ]
            },
        )

    def test_create_profile_with_incorrect_speaking_language(self):
        data = deepcopy(self.correct_data)
        data['speaking_languages'] = ['eo2', 'uk']

        user = UserWithVerifiedEmailFactory()

        client = APIClient()
        self._update_client_with_correct_token(user, client)

        response = client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                'speaking_languages': {
                    0: [
                        ErrorDetail(
                            string='"eo2" is not a valid choice.',
                            code='invalid_choice',
                        )
                    ]
                }
            },
        )

    def test_create_profile_with_subcategories(self):
        subcategory_1 = ServiceFactory()
        subcategory_2 = ServiceFactory()

        data = {
            'name': 'Name',
            'age_above_18': True,
            'agreed_with_conditions': True,
            'gender': 'female',
            'speaking_languages': ['eo', 'uk'],
            'subcategories': [subcategory_1.id, subcategory_2.id],
        }

        user = UserWithVerifiedEmailFactory()

        client = APIClient()
        self._update_client_with_correct_token(user, client)

        response = client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        profile = User.objects.get().profile

        self.assertEqual(
            set(profile.subcategories.values_list('id', flat=True)),
            set(data['subcategories']),
        )

    def test_create_profile_with_non_existing_subcategory(self):
        non_existing_subcategory_id = 100
        self.assertEqual(
            Service.objects.filter(id=non_existing_subcategory_id).count(),
            0,
        )

        data = {
            'name': 'Name',
            'age_above_18': True,
            'agreed_with_conditions': True,
            'gender': 'female',
            'speaking_languages': ['eo', 'uk'],
            'subcategories': [non_existing_subcategory_id],
        }

        user = UserWithVerifiedEmailFactory()

        client = APIClient()
        self._update_client_with_correct_token(user, client)

        response = client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {'subcategories': ['Invalid pk "100" - object does not exist.']},
        )


class SingleProfileViewTestCase(TestCase):
    url = '/users/profile/'

    def _update_client_with_correct_token(self, user, client):
        refresh_token = RefreshToken.for_user(user)

        AUTHORIZATION_HEADER = AUTHORIZATION_HEADER_TEMPLATE.format(
            token=refresh_token.access_token
        )
        client.credentials(HTTP_AUTHORIZATION=AUTHORIZATION_HEADER)

    def test_returns_401_without_token(self):
        client = APIClient()

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_not_exist(self):
        user_without_profile = UserWithVerifiedEmailFactory()

        client = APIClient()
        self._update_client_with_correct_token(user_without_profile, client)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_profile_successful(self):
        service = ServiceFactory()
        EXPECTED_DATA = {
            'name': 'John Doe',
            'age_above_18': True,
            'agreed_with_conditions': True,
            'gender': 'female',
            'speaking_languages': ['eo', 'uk'],
            'subcategories': [service.id],
        }

        user = UserWithProfileFactory(
            profile__name=EXPECTED_DATA['name'],
            profile__age_above_18=EXPECTED_DATA['age_above_18'],
            profile__agreed_with_conditions=EXPECTED_DATA[
                'agreed_with_conditions'
            ],
            profile__gender=EXPECTED_DATA['gender'],
            profile__speaking_languages=EXPECTED_DATA['speaking_languages'],
        )
        user.profile.subcategories.add(service)
        user.profile.save()

        client = APIClient()
        self._update_client_with_correct_token(user, client)

        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, EXPECTED_DATA)
