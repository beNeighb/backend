from rest_framework import serializers
from apps.marketplace.models import Offer


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = '__all__'

    def is_valid(self, *args, **kwargs):
        if hasattr(self.initial_data, '_mutable'):
            self.initial_data._mutable = True
        self.initial_data['helper'] = self.context['request'].user.profile.id
        self.initial_data['status'] = Offer.StatusTypes.PENDING
        return super().is_valid(*args, **kwargs)

    def validate(self, data):
        task = data['task']
        profile_id = self.context['request'].user.profile.id

        self._validate_helper(task, profile_id)
        return super().validate(data)

    def _validate_helper(self, task, profile_id):
        self._validate_not_owner(task, profile_id)
        self._validate_doesnt_have_offer_for_the_task(task, profile_id)

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
