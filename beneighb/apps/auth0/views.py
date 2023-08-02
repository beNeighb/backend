from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from dj_rest_auth.views import PasswordResetConfirmView


class DummyView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        dummy_data = {"message": "This is a dummy response"}
        return Response(dummy_data)


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

