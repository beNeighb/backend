from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

from dj_rest_auth.views import PasswordResetConfirmView, PasswordResetView
from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.registration.serializers import SocialLoginSerializer

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.auth0.adapters import GoogleOAuth2AdapterIdToken


class DummyView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        dummy_data = {"message": "This is a dummy response"}
        return Response(dummy_data)


class BeneighbPasswordResetView(PasswordResetView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        email_address = EmailAddress.objects.get(email=email)

        if not email_address.verified:
            email_address.send_confirmation(request)
            return Response(
                {'detail': 'Verification email has been sent'},
                status=status.HTTP_200_OK,
            )

        return super().post(request, *args, **kwargs)


class BeneighbPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Getting uidb64 and token from the url and updating request.data with them.
    PasswordResetConfirmView expects this job to be done by the FE.
    """

    def post(self, request, *args, **kwargs):
        request_data_copy = request.data.copy()
        token = kwargs.get('token')
        uid = kwargs.get('uidb64')

        request_data_copy['token'] = token
        request_data_copy['uid'] = uid
        # Hack: request.data is immutable
        request._full_data = request_data_copy

        return super().post(request, *args, **kwargs)


class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2AdapterIdToken
    callback_url = 'http://127.0.0.1:8000/auth/login/google/callback/'
    client_class = OAuth2Client
    serializer_class = SocialLoginSerializer
