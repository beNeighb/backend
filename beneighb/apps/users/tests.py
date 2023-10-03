from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.exceptions import ErrorDetail

from apps.users.models import Profile, User
from apps.users.factories import (
    UserWithUnVerifiedEmailFactory,
    UserWithVerifiedEmailFactory,
)


# data = {
#     'name': 'Name',
#     'ageAbove18': True,
#     'agreedWithConditions': True,
#     'gender': 'female',
# }


class CreateProfileTestCase(TestCase):
    url_template = '/users/{0}/create-profile/'

    def test_create_profile_non_existing_user(self):
        self.assertEqual(User.objects.count(), 0)

        data = {
            'name': 'Name',
            'age_above_18': True,
            'agreed_with_conditions': True,
            'gender': 'female',
        }

        url = self.url_template.format(1)

        client = APIClient()
        response = client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_profile_successful(self):
        data = {
            'name': 'Name',
            'age_above_18': True,
            'agreed_with_conditions': True,
            'gender': 'female',
        }

        user = UserWithVerifiedEmailFactory()
        url = self.url_template.format(user.id)

        client = APIClient()
        response = client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(User.objects.count(), 1)

        user = User.objects.get()
        profile = user.profile

        self.assertEqual(type(profile), Profile)
        self.assertEqual(profile.name, 'Name')
        self.assertEqual(profile.age_above_18, True)
        self.assertEqual(profile.agreed_with_conditions, True)
        self.assertEqual(profile.gender, 'female')

    def test_create_profile_without_name(self):
        data = {
            'age_above_18': True,
            'agreed_with_conditions': True,
            'gender': 'female',
        }

        user = UserWithVerifiedEmailFactory()
        url = self.url_template.format(user.id)

        client = APIClient()
        response = client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                'name': [
                    ErrorDetail(
                        string='This field is required.', code='required'
                    )
                ]
            },
        )

    def test_create_profile_without_age_above_18(self):
        data = {
            'name': 'Name',
            'agreed_with_conditions': True,
            'gender': 'female',
        }

        user = UserWithVerifiedEmailFactory()
        url = self.url_template.format(user.id)

        client = APIClient()
        response = client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                'age_above_18': [
                    ErrorDetail(
                        string='This field is required.', code='required'
                    )
                ]
            },
        )

    def test_create_profile_without_agreed_with_conditions(self):
        data = {
            'name': 'Name',
            'age_above_18': True,
            'gender': 'female',
        }

        user = UserWithVerifiedEmailFactory()
        url = self.url_template.format(user.id)

        client = APIClient()
        response = client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                'agreed_with_conditions': [
                    ErrorDetail(
                        string='This field is required.', code='required'
                    )
                ]
            },
        )

    def test_create_profile_without_gender(self):
        data = {
            'name': 'Name',
            'age_above_18': True,
            'agreed_with_conditions': True,
        }

        user = UserWithVerifiedEmailFactory()
        url = self.url_template.format(user.id)

        client = APIClient()
        response = client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                'gender': [
                    ErrorDetail(
                        string='This field is required.', code='required'
                    )
                ]
            },
        )

    def test_create_profile_with_incorrect_gender(self):
        data = {
            'name': 'Name',
            'age_above_18': True,
            'agreed_with_conditions': True,
            'gender': 'female2',
        }

        user = UserWithVerifiedEmailFactory()
        url = self.url_template.format(user.id)

        client = APIClient()
        response = client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                'gender': [
                    ErrorDetail(
                        string='"female2" is not a valid choice.', code='invalid_choice'
                    )
                ]
            },
        )
