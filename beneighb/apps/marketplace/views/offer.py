import logging

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.marketplace.models import Offer
from apps.marketplace.serializers import OfferSerializer

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
