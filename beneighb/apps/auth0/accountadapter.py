from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        return settings.CUSTOM_ACCOUNT_CONFIRM_EMAIL_URL.format(
            emailconfirmation.key
        )

    def send_mail(self, template_prefix, *args, **kwargs):
        template_prefix = 'account/email/custom_password_reset_key'
        super().send_mail(template_prefix, *args, **kwargs)
