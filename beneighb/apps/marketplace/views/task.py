import logging
from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from apps.marketplace.permissions import IsIdempotent
from apps.marketplace.models import Offer, Task
from apps.marketplace.serializers import (
    TaskCreateSerializer,
    TaskWithOffersSerializer,
)
from apps.users.models import Profile
from apps.users.notifications import send_push_notification

logger = logging.getLogger(__name__)


class TaskCreateView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsIdempotent)
    serializer_class = TaskCreateSerializer
    queryset = Task.objects.all()

    def perform_create(self, serializer):
        task = serializer.save()
        text = f'New task has been created: {task.service.name}'
        data = {
            'type': 'new_task',
            'task_id': str(task.id),
        }

        # task_service = task.service
        recipients = (
            Profile.objects.all()
            # TODO: Uncomment this, during #284 - add back filters for services
            # with corresponding services
            # Profile.objects.filter(services=task_service)
            .exclude(id=task.owner.id)
            .exclude(fcm_token='')
            .exclude(fcm_token__isnull=True)
        )

        for recipient in recipients:
            # PERFORMANCE: This is not optimal: Use celery and topics instead
            send_push_notification(recipient, text, data=data)


class TaskMineListView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskWithOffersSerializer

    def get_queryset(self):
        profile = self.request.user.profile
        return Task.objects.filter(owner=profile)


class TaskForMeListView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskWithOffersSerializer

    def get_blocking_owners_ids(self, user):
        return user.profile.blocked_profiles.values_list(
            'blocking_profile_id', flat=True
        )

    def get_queryset(self):
        user = self.request.user
        # TODO: Check if can be optimized
        # user_services = user.profile.services.all()
        # return Task.objects.filter(service__in=user_services).exclude(
        #     owner=user.profile
        # )
        # TODO: Uncomment this, during #284 - add back filters for services

        ONLINE_EVENT = Task.EventTypes.ONLINE

        tasks = Task.objects.all().exclude(owner=user.profile)
        blocking_owners_ids = self.get_blocking_owners_ids(user)
        tasks = tasks.exclude(owner__id__in=blocking_owners_ids)

        tasks = tasks.filter(
            Q(owner__city=user.profile.city) | Q(event_type=ONLINE_EVENT)
        )

        return tasks


class TaskWithMyOfferListView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskWithOffersSerializer

    def get_queryset(self):
        user = self.request.user

        my_offers = Offer.objects.filter(helper=user.profile)
        task_ids = [offer.task.id for offer in my_offers]

        return Task.objects.filter(id__in=task_ids)


class TaskRetrieveView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskWithOffersSerializer
    queryset = Task.objects.all()

    def _is_blocked_by_owner(self):
        task_id = self.kwargs.get('pk')
        task = get_object_or_404(self.queryset, id=task_id)
        owner_profile = task.owner

        helper_profile = self.request.user.profile

        return owner_profile.blocking_profiles.filter(
            blocked_profile=helper_profile
        ).exists()

    def get_queryset(self):
        is_blocked_by_owner = self._is_blocked_by_owner()

        if is_blocked_by_owner:
            raise PermissionDenied()

        return self.queryset
