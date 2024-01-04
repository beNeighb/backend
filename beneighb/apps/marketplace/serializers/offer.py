from rest_framework import serializers

from apps.chat.serializers import ChatSerializer

from apps.users.serializers import ShortProfileSerializer
from apps.marketplace.models import Offer


class OfferWithHelperSerializer(serializers.ModelSerializer):
    helper = ShortProfileSerializer(read_only=True)

    class Meta:
        model = Offer
        fields = ('id', 'helper', 'status', 'created_at')


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = (
            'id',
            'task',
            'helper',
            'status',
            'created_at',
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

        self._validate_status(data)
        self._validate_helper(task, profile_id)
        return super().validate(data)

    def _validate_status(self, data):
        if data.get('status') == Offer.StatusTypes.PENDING:
            return

        if self.instance is None:
            raise serializers.ValidationError(
                {
                    'status': 'You cannot create offer with status=accepted',  # noqa
                }
            )

        accepted_offers = self.instance.task.offer_set.filter(
            status=Offer.StatusTypes.ACCEPTED
        ).exclude(id=self.instance.id)

        if accepted_offers.exists():
            raise serializers.ValidationError(
                {
                    'status': 'You cannot set status=accepted because there is already accepted offer for this task.'  # noqa
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
        tasks_qs = task.offer_set.filter(helper=profile_id)
        if self.instance:
            tasks_qs = tasks_qs.exclude(id=self.instance.id)

        if tasks_qs.exists():
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


class OfferAcceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = (
            'id',
            'task',
            'helper',
            'status',
            'created_at',
        )

    def __init__(self, instance, data, **kwargs):
        super().__init__(instance, data, **kwargs)

        self.owner = self.context['request'].user.profile
        self.task = instance.task

    def validate(self, data):
        self._validate_status(data)
        self._validate_helper_owns_task()
        return super().validate(data)

    def _validate_status(self, data):
        accepted_offers = self.instance.task.offer_set.filter(
            status=Offer.StatusTypes.ACCEPTED
        ).exclude(id=self.instance.id)

        if accepted_offers.exists():
            raise serializers.ValidationError(
                {
                    'status': 'You cannot set status=accepted because there is already accepted offer for this task.'  # noqa
                }
            )

    def _validate_helper_owns_task(self):
        if self.instance.task.owner.id != self.owner.id:
            raise serializers.ValidationError(
                "You cannot accept another offer for another user's task."
            )


class OfferSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = (
            'id',
            'task',
            'helper',
            'status',
            'created_at',
        )


class OfferWithChatSerializer(serializers.Serializer):
    offer = OfferSimpleSerializer(read_only=True)
    chat = ChatSerializer(read_only=True)

    class Meta:
        fields = (
            'offer',
            'chat',
        )
