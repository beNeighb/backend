from allauth.account.models import EmailAddress

from factory import Faker, post_generation, Sequence
from factory.django import DjangoModelFactory

from apps.users.models import User


class EmailFactory(DjangoModelFactory):
    class Meta:
        model = EmailAddress

    email = Faker('email')
    verified = False


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = Sequence(lambda n: 'test_user{}'.format(n))
    email = Faker('email')


class UserWithUnVerifiedEmailFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = Sequence(lambda n: 'test_user{}'.format(n))
    email = Faker('email')

    @post_generation
    def create_email_address(self, created, extracted, **kwargs):
        EmailAddress.objects.create(user=self, email=self.email, verified=False)


class UserWithVerifiedEmailFactory(UserWithUnVerifiedEmailFactory):
    @post_generation
    def create_email_address(self, created, extracted, **kwargs):
        EmailAddress.objects.create(user=self, email=self.email, verified=True)
