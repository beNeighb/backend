from rest_framework import serializers
from apps.marketplace.models import Offer
from apps.users.serializers import ShortProfileSerializer


class OfferWithHelperSerializer(serializers.ModelSerializer):
    helper = ShortProfileSerializer(read_only=True)

    class Meta:
        model = Offer
        fields = ('id', 'helper', 'status', 'created_at', 'is_accepted')


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = (
            'id',
            'task',
            'helper',
            'status',
            'created_at',
            'is_accepted',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.context['request'].user.profile

    def is_valid(self, *args, **kwargs):
        if hasattr(self.initial_data, '_mutable'):
            self.initial_data._mutable = True

        self.initial_data['helper'] = self.helper.id
        self.initial_data['status'] = Offer.StatusTypes.PENDING
        return super().is_valid(*args, **kwargs)

    def validate(self, data):
        task = data['task']
        profile_id = self.helper.id

        self._validate_is_accepted(data)
        self._validate_helper(task, profile_id)
        return super().validate(data)

    def _validate_is_accepted(self, data):
        if self.instance is None:
            if data.get('is_accepted', True):
                raise serializers.ValidationError(
                    {
                        'is_accepted': 'You cannot create offer with is_accepted=True',
                    }
                )

    def _validate_helper(self, task, profile_id):
        self._validate_not_owner(task, profile_id)
        self._validate_doesnt_have_offer_for_the_task(task, profile_id)
        self._validate_helper_has_matching_service(task, profile_id)

    def _validate_not_owner(self, task, profile_id):
        if task.owner.id == profile_id:
            raise serializers.ValidationError(
                'You can not offer to help your own task'
            )

    def _validate_doesnt_have_offer_for_the_task(self, task, profile_id):
        if task.offer_set.filter(helper=profile_id).count():
            raise serializers.ValidationError(
                ['Only one offer is allowed per task.']
            )

    def _validate_helper_has_matching_service(self, task, profile_id):
        if task.service not in self.helper.services.all():
            raise serializers.ValidationError(
                [
                    'You cannot create offer because you do not have a matching service.'  # noqa
                ]
            )
