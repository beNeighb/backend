from datetime import datetime, timezone
from operator import add
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

    class Meta:
        model = Task
        fields = '__all__'

    def validate(self, data):
        datetime_known = data['datetime_known']
        datetime_options = data.get('datetime_options')

        self._validate_datetime_options(datetime_known, datetime_options)

        event_type = data['event_type']
        address = data.get('address')

        self._validate_event_type_address(event_type, address)

        price_offer = data['price_offer']
        self._validate_price_offer(price_offer)

        return super().validate(data)

    @classmethod
    def _validate_datetime_options(cls, datetime_known, datetime_options):
        def _is_date_in_future(dt_option):
            return dt_option > datetime.now(tz=timezone.utc)

        if not datetime_known:
            if not datetime_options:
                raise serializers.ValidationError(
                    {
                        'datetime_options': 'datetime_options is required when date_timeknow is False'
                    }
                )
            else:
                for option in datetime_options:
                    if not _is_date_in_future(option):
                        raise serializers.ValidationError(
                            {
                                'datetime_options': 'All datetime_options should be in the future'
                            }
                        )
        else:
            if datetime_options:
                raise serializers.ValidationError(
                    {
                        'datetime_options': 'For datetime_known=True datetime_options should be empty'
                    }
                )

    @classmethod
    def _validate_event_type_address(cls, event_type, address):
        if event_type == Task.EventTypes.ONLINE:
            if address:
                raise serializers.ValidationError(
                    {
                        'address': "For event_type=online address shouldn't be present",
                    }
                )
        else:
            if not address:
                raise serializers.ValidationError(
                    {
                        'address': 'For event_type=offline address is required',
                    }
                )

    @classmethod
    def _validate_price_offer(cls, price_offer):
        if price_offer <= 0:
            raise serializers.ValidationError(
                {
                    'price_offer': 'price_offer should be greater than 0',
                }
            )
