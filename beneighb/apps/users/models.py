from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField


class Genders(models.TextChoices):
    MALE = 'male', _('Male')
    FEMALE = 'female', _('Female')
    OTHER = 'other', _('Other')


class LanguageChoices(models.TextChoices):
    ESPERANTO = 'eo', 'Esperanto'
    UKRAINIAN = 'uk', 'Ukrainian'
    ENGLISH = 'en', 'English'
    ARABIC = 'ar', 'Arabic'
    FRENCH = 'fr', 'French'
    SPANISH = 'es', 'Spanish'
    GERMAN = 'de', 'German'
    ITALIAN = 'it', 'Italian'
    CHINESE = 'zh', 'Chinese'
    JAPANESE = 'ja', 'Japanese'
    KOREAN = 'ko', 'Korean'
    PORTUGUESE = 'pt', 'Portuguese'
    TURKISH = 'tr', 'Turkish'
    POLISH = 'pl', 'Polish'
    RUSSIAN = 'ru', 'Russian'


class Profile(models.Model):
    """
    This model is used for non-auth/login related fields.
    """

    name = models.CharField(
        max_length=150,
        blank=False,
    )
    age_above_18 = models.BooleanField(blank=False)
    agreed_with_conditions = models.BooleanField(blank=False)
    gender = models.CharField(
        max_length=6,
        choices=Genders.choices,
        blank=False,
    )
    speaking_languages = ArrayField(
        models.CharField(
            choices=LanguageChoices.choices,
            max_length=2,
            blank=False,
        )
    )

    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    This model is used for auth/login related fields.
    """

    username = models.CharField(
        max_length=150,
        null=True,
        blank=True,
    )
    email = models.EmailField(unique=True)
    profile = models.OneToOneField(
        Profile, on_delete=models.CASCADE, null=True, blank=True
    )

    @property
    def email_verified(self):
        verified = False
        email = self.emailaddress_set.first()
        if email:
            verified = email.verified
        return verified


"""receivers to add a Profile for newly created users"""


# TODO: Move to save or _create_user
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.profile:
        instance.profile.save()
