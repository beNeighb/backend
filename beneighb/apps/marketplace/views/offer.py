import logging

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.marketplace.models import Assignment, Chat, Offer
from apps.marketplace.serializers import (
    OfferAcceptSerializer,
    OfferSerializer,
    OfferWithChatSerializer,
)

logger = logging.getLogger(__name__)


class OfferCreateView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OfferSerializer
    queryset = Offer.objects.all()


class OfferMineListView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OfferSerializer

    def get_queryset(self):
        my_profile = self.request.user.profile
        return Offer.objects.filter(helper=my_profile)


class OfferAcceptView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OfferAcceptSerializer
    queryset = Offer.objects.all()

    def update(self, request, *args, **kwargs):
        offer_instance = self.get_object()
        data = {'status': Offer.StatusTypes.ACCEPTED}

        serializer = self.get_serializer(
            offer_instance, data=data, partial=True
        )
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        assignment = Assignment.objects.create(offer=offer_instance)
        chat_instance = Chat.objects.create(assignment=assignment)

        serializer = OfferWithChatSerializer(
            {'offer': offer_instance, 'chat': chat_instance}, data={}
        )
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data)
