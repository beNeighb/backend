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
    AFRIKAANS = ('af', 'Afrikaans')
    ARABIC = ('ar', 'Arabic')
    ARMENIAN = ('hy', 'Armenian')
    BENGALI = ('bn', 'Bengali')
    BULGARIAN = ('bg', 'Bulgarian')
    CHINESE = ('zh', 'Chinese')
    CROATIAN = ('hr', 'Croatian')
    CZECH = ('cs', 'Czech')
    DANISH = ('da', 'Danish')
    DUTCH = ('nl', 'Dutch')
    ENGLISH = ('en', 'English')
    ESTONIAN = ('et', 'Estonian')
    ESPERANTO = ('eo', 'Esperanto')
    FARSI = ('fa', 'Farsi')
    FINNISH = ('fi', 'Finnish')
    FRENCH = ('fr', 'French')
    GEORGIAN = ('ka', 'Georgian')
    GERMAN = ('de', 'German')
    GREEK = ('el', 'Greek')
    HINDI = ('hi', 'Hindi')
    HUNGARIAN = ('hu', 'Hungarian')
    INDONESIAN = ('id', 'Indonesian')
    ITALIAN = ('it', 'Italian')
    JAPANESE = ('ja', 'Japanese')
    KAZAKH = ('kk', 'Kazakh')
    KOREAN = ('ko', 'Korean')
    KURDISH = ('ku', 'Kurdish')
    MACEDONIAN = ('mk', 'Macedonian')
    NORWEGIAN = ('no', 'Norwegian')
    POLISH = ('pl', 'Polish')
    PORTUGUESE = ('pt', 'Portuguese')
    ROMANIAN = ('ro', 'Romanian')
    RUSSIAN = ('ru', 'Russian')
    SLOVAK = ('sk', 'Slovak')
    SLOVENIAN = ('sl', 'Slovenian')
    SPANISH = ('es', 'Spanish')
    SWEDISH = ('sv', 'Swedish')
    THAI = ('th', 'Thai')
    TURKISH = ('tr', 'Turkish')
    UKRAINIAN = ('uk', 'Ukrainian')
    URDU = ('ur', 'Urdu')
    UZBEK = ('uz', 'Uzbek')
    VIETNAMESE = ('vi', 'Vietnamese')


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
    subcategories = models.ManyToManyField(
        'marketplace.Subcategory', related_name='subcategories', blank=False
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
