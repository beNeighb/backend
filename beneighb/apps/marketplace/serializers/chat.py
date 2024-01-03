from rest_framework import serializers
from apps.marketplace.models import Chat


class ChatSerializer(serializers.ModelSerializer):
    service = serializers.IntegerField(
        source='assignment.offer.task.service.id'
    )
    profile_name = serializers.SerializerMethodField()
    offer = serializers.IntegerField(source='assignment.offer.id')

    last_message_sent_at = serializers.DateTimeField(default='2024-01-03')
    # last_message_sent_at = serializers.DateTimeField(source='created_at')
    unread_messages_count = serializers.IntegerField(default=42)

    def get_profile_name(self, obj):
        my_profile = self.context['request'].user.profile

        task_owner = obj.assignment.offer.task.owner
        offer_helper = obj.assignment.offer.helper

        return (
            offer_helper.name if my_profile == task_owner else task_owner.name
        )

    class Meta:
        model = Chat
        fields = (
            'id',
            'created_at',
            'offer',
            'service',
            'profile_name',
            'last_message_sent_at',
            'unread_messages_count',
        )


class ShortChatSerializer(serializers.ModelSerializer):
    service = serializers.IntegerField(
        source='assignment.offer.task.service.id'
    )
    profile_name = serializers.SerializerMethodField()
    offer = serializers.IntegerField(source='assignment.offer.id')

    def get_profile_name(self, obj):
        my_profile = self.context['request'].user.profile

        task_owner = obj.assignment.offer.task.owner
        offer_helper = obj.assignment.offer.helper

        return (
            offer_helper.name if my_profile == task_owner else task_owner.name
        )

    class Meta:
        model = Chat
        fields = (
            'id',
            'created_at',
            'offer',
            'service',
            'profile_name',
        )
