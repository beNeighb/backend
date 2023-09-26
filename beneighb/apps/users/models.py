from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        null=True,
        blank=True,
    )
    email = models.EmailField(unique=True)

    @property
    def email_verified(self):
        verified = False
        email = self.emailaddress_set.first()
        if email:
            verified = email.verified
        return verified
