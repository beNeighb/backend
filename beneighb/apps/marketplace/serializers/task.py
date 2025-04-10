from datetime import datetime, timezone
from rest_framework import serializers
from apps.marketplace.models import Task
from apps.marketplace.serializers.offer import OfferWithHelperSerializer


# TODO: Move this class to some utils to reuse in all apps
class RequirableBooleanField(serializers.BooleanField):
    """
    Making BooleanField respect required=True.
    """

    default_empty_html = serializers.empty


class TaskWithOffersSerializer(serializers.ModelSerializer):
    datetime_known = RequirableBooleanField(required=True)
    offers = OfferWithHelperSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = Task
        fields = (
            'id',
            'created_at',
            'service',
            'owner',
            'datetime_known',
            'datetime_options',
            'event_type',
            'address',
            'price_offer',
            'offers',
            'info',
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        current_user = self.context['request'].user.profile

        offers = instance.offers.all()
        if instance.owner != current_user:
            offers = instance.offers.filter(helper=current_user)

        offer_serializer = OfferWithHelperSerializer(offers, many=True)
        representation['offers'] = offer_serializer.data
        return representation


class TaskCreateSerializer(serializers.ModelSerializer):
    datetime_known = RequirableBooleanField(required=True)
    offers = OfferWithHelperSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = Task
        fields = '__all__'

    def is_valid(self, *args, **kwargs):
        # Setting owner of the task to current user's profile
        # For some reason on production self.initial_data is a regular dict
        if hasattr(self.initial_data, '_mutable'):
            self.initial_data._mutable = True
        self.initial_data['owner'] = self.context['request'].user.profile.id
        return super().is_valid(*args, **kwargs)

    def validate(self, data):
        datetime_known = data['datetime_known']
        datetime_options = data.get('datetime_options')

        self._validate_datetime_options(datetime_known, datetime_options)

        if 'info' in data:
            self._validate_info(data['info'])

        event_type = data['event_type']
        address = data.get('address')

        self._validate_event_type_address(event_type, address)

        price_offer = data['price_offer']
        self._validate_price_offer(price_offer)

        return super().validate(data)

    def _validate_info(self, info):
        if info is None:
            return

        if len(info) > 140:
            raise serializers.ValidationError(
                {'info': 'Info should be less than 140 characters'}
            )

        if not info.strip():
            raise serializers.ValidationError(
                {'info': 'Info should not be empty or contain only whitespaces'}
            )

    @classmethod
    def _validate_datetime_options(cls, datetime_known, datetime_options):
        def _is_date_in_future(dt_option):
            return dt_option > datetime.now(tz=timezone.utc)

        if datetime_known:
            if not datetime_options:
                raise serializers.ValidationError(
                    {
                        'datetime_options': (
                            'datetime_options is required'
                            ' when date_timeknow is True'
                        )
                    }
                )
            else:
                for option in datetime_options:
                    if not _is_date_in_future(option):
                        raise serializers.ValidationError(
                            {
                                'datetime_options': (
                                    'All datetime_options '
                                    'should be in the future'
                                )
                            }
                        )
        else:
            if datetime_options:
                raise serializers.ValidationError(
                    {
                        'datetime_options': (
                            'For datetime_known=False '
                            'datetime_options should be empty'
                        )
                    }
                )

    @classmethod
    def _validate_event_type_address(cls, event_type, address):
        if event_type == Task.EventTypes.ONLINE:
            if address:
                raise serializers.ValidationError(
                    {
                        'address': (
                            "For event_type=online address "
                            "shouldn't be present"
                        ),
                    }
                )
        else:
            if not address:
                raise serializers.ValidationError(
                    {
                        'address': (
                            'For event_type=offline address ' 'is required'
                        ),
                    }
                )

    @classmethod
    def _validate_price_offer(cls, price_offer):
        if price_offer < 0:
            raise serializers.ValidationError(
                {
                    'price_offer': 'price_offer cannot be negative',
                }
            )
