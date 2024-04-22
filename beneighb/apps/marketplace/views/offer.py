import logging

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.chat.models import Chat
from apps.marketplace.models import Assignment, Offer
from apps.marketplace.serializers import (
    OfferAcceptSerializer,
    OfferSerializer,
    OfferWithChatSerializer,
)
from apps.users.notifications import send_push_notification

logger = logging.getLogger(__name__)


class OfferCreateView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OfferSerializer
    queryset = Offer.objects.all()

    def perform_create(self, serializer):
        offer = serializer.save()
        send_push_notification(
            offer.task.owner,
            'You have a new offer!',
            data={
                'type': 'new_offer',
                'task_id': str(offer.task.id),
            },
        )


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

        assignment = Assignment.objects.get_or_create(offer=offer_instance)

        serializer = OfferWithChatSerializer(
            {'offer': offer_instance, 'chat': offer_instance.chat},
            data={},
            context={'request': request},
        )
        serializer.is_valid()

        send_push_notification(
            offer_instance.helper,
            'Your offer has been accepted!',
            data={
                'type': 'offer_accepted',
                'chat_id': str(offer_instance.chat.id),
            },
        )

        return Response(serializer.data)
