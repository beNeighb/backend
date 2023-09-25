from django.contrib.sites.shortcuts import get_current_site
from dj_rest_auth.forms import AllAuthPasswordResetForm

from allauth.account.forms import default_token_generator
from allauth.account.utils import filter_users_by_email, user_pk_to_url_str
from allauth.account.adapter import get_adapter


class CustomAllAuthPasswordResetForm(AllAuthPasswordResetForm):
    def clean_email(self):
        """
        Invalid email should not raise error, as this would leak users
        for unit test: test_password_reset_with_invalid_email
        """
        email = self.cleaned_data['email']
        email = get_adapter().clean_email(email)
        self.users = filter_users_by_email(email, is_active=True)
        return self.cleaned_data['email']

    def save(self, request, **kwargs):
        current_site = get_current_site(request)
        email = self.cleaned_data['email']
        token_generator = kwargs.get(
            'token_generator', default_token_generator
        )

        for user in self.users:
            token = token_generator.make_token(user)

            # Hack: getting 'link.beneighb.com' instead of 'api...' or test
            url = (
                'https://link.beneighb.com/auth/password-reset-confirm/'
                f'{user_pk_to_url_str(user)}/{token}/'
            )

            # Values which are passed to custom_password_reset_key_message.html
            context = {
                'current_site': current_site,
                'user': user,
                'password_reset_url': url,
                'request': request,
            }

            get_adapter(request).send_mail(
                'account/email/password_reset_key', email, context
            )

        return self.cleaned_data['email']
