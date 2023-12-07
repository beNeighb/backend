import logging
from django.core.cache import cache
from rest_framework.permissions import BasePermission


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
