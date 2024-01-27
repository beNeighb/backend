from django.db import transaction
from rest_framework import serializers
from apps.chat.models import Chat, Message


class MessageSerializer(serializers.ModelSerializer):
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = (
            'id',
            'chat',
            'sent_at',
            'read_at',
            'is_mine',
            'text',
        )

    def get_is_mine(self, obj):
        return self.context['request'].user.profile == obj.sender


class MessageCreateSerializer(serializers.ModelSerializer):
    is_mine = serializers.SerializerMethodField()
    sender = serializers.IntegerField(source='sender_id', write_only=True)
    recipient = serializers.IntegerField(
        source='recipient_id', write_only=True
    )

    class Meta:
        model = Message
        fields = (
            'id',
            'chat',
            'sent_at',
            'read_at',
            'is_mine',
            'sender',
            'recipient',
            'text',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # For testing only
        if hasattr(self.initial_data, '_mutable'):
            self.initial_data._mutable = True

        current_profile = self.context['request'].user.profile

        self.initial_data['sender'] = current_profile.id
        self.initial_data['recipient'] = self.get_receipient(
            current_profile
        ).id
        self.initial_data['chat'] = self.context['view'].kwargs['chat_id']

    def get_receipient(self, sender):
        chat_id = self.context['view'].kwargs['chat_id']
        chat = Chat.objects.get(id=chat_id)
        task_owner = chat.assignment.offer.task.owner
        helper = chat.assignment.offer.helper

        if sender == task_owner:
            return helper
        elif sender == helper:
            return task_owner
        else:
            raise serializers.ValidationError(
                {'sender': 'You are not a member of this chat.'},
            )

    def get_is_mine(self, obj):
        return self.context['request'].user.profile == obj.sender


class MessageMarkAsReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'read_at')
        read_only_fields = ('id',)

    def validate(self, data):
        if 'read_at' not in data or not data['read_at']:
            raise serializers.ValidationError(
                {'read_at': "Field 'read_at' cannot be missing or empty."},
            )

        return data

    def update(self, instance, validated_data):
        my_profile = self.context['request'].user.profile
        chat_messages = instance.chat.messages.all()

        unread_msgs = chat_messages.exclude(sender=my_profile).filter(
            read_at=None,
            sent_at__lte=instance.sent_at,
        )

        if unread_msgs.exists():
            with transaction.atomic():
                unread_msgs.update(read_at=validated_data.get('read_at'))
                instance.refresh_from_db()

        return instance
