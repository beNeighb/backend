import logging

from django.core.cache import cache

from apps.marketplace.models import Task
from apps.marketplace.serializers import TaskSerializer

from rest_framework import generics
from rest_framework.permissions import BasePermission, IsAuthenticated

logger = logging.getLogger(__name__)


class IsIdempotent(BasePermission):
    message = 'Duplicate request detected.'

    def has_permission(self, request, view):
        if request.method != 'POST':
            return True

        header_key = request.META.get('HTTP_X_IDEMPOTENCY_KEY')
        if header_key is None:
            return True

        key = f'idemp-{request.user.pk}-{header_key}'
        is_idempotent = bool(cache.add(key, 1))

        if not is_idempotent:
            logger.info(f'Duplicate request (non-idempotent): key={key}')
        return is_idempotent


class TaskCreateView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsIdempotent)
    serializer_class = TaskSerializer
    queryset = Task.objects.all()


class TaskMineListView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)


class TaskForMeListView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        user_services = user.profile.services.all()
        # TODO: Check if can be optimized
        return Task.objects.filter(service__in=user_services)


class TaskRetrieveView(generics.RetrieveAPIView):
    queryset = Task.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskSerializer
