from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status


from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer


class DummyView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        dummy_data = {"message": "This is a dummy response"}
        return Response(dummy_data)
