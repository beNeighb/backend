from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class DummyView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        dummy_data = {"message": "This is a dummy response"}
        return Response(dummy_data)
