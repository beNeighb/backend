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
        if task.offer_set.filter(helper=profile_id).count():
            raise serializers.ValidationError(
                ['Only one offer is allowed per task.']
            )

        return super().validate(data)
