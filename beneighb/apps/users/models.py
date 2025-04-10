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


class Cities(models.TextChoices):
    DUSSELDORF = 'Dusseldorf', _('Dusseldorf')
    BERLIN = 'Berlin', _('Berlin')


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
    fcm_token = models.CharField(max_length=255, blank=True)
    services = models.ManyToManyField('marketplace.Service', blank=True)

    city = models.CharField(
        max_length=50,
        choices=Cities.choices,
        blank=False,
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

    def __str__(self):
        return self.email


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.profile:
        instance.profile.save()


class Block(models.Model):
    blocked_profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='blocked_profiles'
    )
    blocking_profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='blocking_profiles'
    )

    class Meta:
        unique_together = ('blocked_profile', 'blocking_profile')

    def __str__(self):
        return f'{self.blocked_profile} is blocked by {self.blocking_profile}'
