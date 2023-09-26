from allauth.account.adapter import DefaultAccountAdapter

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        return settings.CUSTOM_ACCOUNT_CONFIRM_EMAIL_URL.format(
            emailconfirmation.key
        )

    # TODO: Delete if not needed
    def send_mail(self, template_prefix, *args, **kwargs):
        # template_prefix = 'account/email/custom_password_reset_key'
        super().send_mail(template_prefix, *args, **kwargs)

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        """
        Need this method to change email_template to a link_*.
        """

        current_site = get_current_site(request)
        activate_url = self.get_email_confirmation_url(
            request, emailconfirmation
        )
        ctx = {
            "user": emailconfirmation.email_address.user,
            "activate_url": activate_url,
            "current_site": current_site,
            "key": emailconfirmation.key,
        }

        if signup:
            email_template = "account/email/link_email_confirmation_signup"
        else:
            email_template = "account/email/link_email_confirmation"

        self.send_mail(
            email_template, emailconfirmation.email_address.email, ctx
        )
