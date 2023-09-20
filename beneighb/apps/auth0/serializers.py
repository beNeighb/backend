from django.conf import settings
from rest_framework import exceptions
from dj_rest_auth.serializers import PasswordResetSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from allauth.account.models import EmailAddress


class LinkPasswordResetSerializer(PasswordResetSerializer):
    def get_email_options(self):
        extra_context = {
            'email_site_name': 'Beneighb',
            'site_protocol': settings.SITE_PROTOCOL,
        }

        return {
            'domain_override': settings.SITE_LINK_URL,
            'email_template_name': 'reset_password_email.html',
            # We'll need it for sure
            # 'html_email_template_name': 'reset_password_email.html',
            'extra_email_context': extra_context,
            'subject_template_name': 'password_reset_subject.txt',
        }


class VerifiedEmailSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        try:
            email = attrs.get('username')
            email = EmailAddress.objects.get(email=email)
            if not email.verified:
                raise exceptions.AuthenticationFailed(
                    'Sorry, but you can only login with verified email',
                    'email_not_verified',
                )
        except EmailAddress.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                self.error_messages['no_active_account'],
                'no_active_account',
            )

        return super().validate(attrs)
