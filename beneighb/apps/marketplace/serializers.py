from rest_framework import serializers
from apps.marketplace.models import Task


# TODO: Move this class to some utils to reuse in all apps
class RequirableBooleanField(serializers.BooleanField):
    """
    Making BooleanField respect required=True.
    """

    default_empty_html = serializers.empty


class TaskSerializer(serializers.ModelSerializer):
    datetime_known = RequirableBooleanField(required=True)
    # agreed_with_conditions = RequirableBooleanField(required=True)

    class Meta:
        model = Task
        fields = [
            'created_at',
            'service',
            'datetime_known',
            'datetime_options',
            'event_type',
            'address',
            'price_offer',
        ]
