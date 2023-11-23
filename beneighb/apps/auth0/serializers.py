from rest_framework import exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from allauth.account.models import EmailAddress

from dj_rest_auth import serializers
from dj_rest_auth.serializers import PasswordResetSerializer

from apps.auth0.forms import CustomAllAuthPasswordResetForm


class LinkPasswordResetSerializer(PasswordResetSerializer):
    def validate_email(self, value):
        # Use the custom reset form
        self.reset_form = CustomAllAuthPasswordResetForm(
            data=self.initial_data
        )
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)

        return value


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
