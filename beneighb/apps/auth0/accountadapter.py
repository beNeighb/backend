from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        return settings.CUSTOM_ACCOUNT_CONFIRM_EMAIL_URL.format(
            emailconfirmation.key
        )
