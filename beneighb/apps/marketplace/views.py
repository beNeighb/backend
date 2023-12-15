import logging

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.marketplace.permissions import IsIdempotent
from apps.marketplace.models import Offer, Task
from apps.marketplace.serializers import (
    OfferSerializer,
    TaskCreateSerializer,
    TaskWithOffersSerializer,
)

logger = logging.getLogger(__name__)


class TaskCreateView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsIdempotent)
    serializer_class = TaskCreateSerializer
    queryset = Task.objects.all()


class TaskMineListView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskWithOffersSerializer

    def get_queryset(self):
        profile = self.request.user.profile
        return Task.objects.filter(owner=profile)


class TaskForMeListView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskWithOffersSerializer

    def get_queryset(self):
        user = self.request.user
        user_services = user.profile.services.all()
        # TODO: Check if can be optimized
        return Task.objects.filter(service__in=user_services).exclude(
            owner=user.profile
        )


class TaskWithMyOfferListView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskWithOffersSerializer

    def get_queryset(self):
        user = self.request.user

        my_offers = Offer.objects.filter(helper=user.profile)
        task_ids = [offer.task.id for offer in my_offers]

        return Task.objects.filter(id__in=task_ids)


class TaskRetrieveView(generics.RetrieveAPIView):
    queryset = Task.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskWithOffersSerializer


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
