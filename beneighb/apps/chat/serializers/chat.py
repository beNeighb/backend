from rest_framework import serializers
from apps.chat.models import Chat, Message


class BaseChatSerializer(serializers.ModelSerializer):
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


class ChatSerializer(BaseChatSerializer):
    pass


class ChatWithMessageDataSerializer(BaseChatSerializer):
    last_message_sent_at = serializers.DateTimeField(default='2024-01-03')
    unread_messages_count = serializers.IntegerField(default=42)

    class Meta(BaseChatSerializer.Meta):
        fields = BaseChatSerializer.Meta.fields + (
            'last_message_sent_at',
            'unread_messages_count',
        )


class MessageSerializer(serializers.ModelSerializer):
    is_mine = serializers.SerializerMethodField()
    author = serializers.IntegerField(source='author_id', write_only=True)

    class Meta:
        model = Message
        fields = (
            'id',
            'chat',
            'sent_at',
            'read_at',
            'is_mine',
            'author',
            'text',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if hasattr(self.initial_data, '_mutable'):
            self.initial_data._mutable = True

        self.initial_data['author'] = self.context['request'].user.profile.id
        self.initial_data['chat'] = self.context['view'].kwargs['chat_id']

    def get_is_mine(self, obj):
        return self.context['request'].user.profile == obj.author

    # def is_valid(self, *args, **kwargs):
    #     if hasattr(self.initial_data, '_mutable'):
    #         self.initial_data._mutable = True

    #     self.initial_data['helper'] = self.helper.id
    #     self.initial_data['status'] = Offer.StatusTypes.PENDING
    #     return super().is_valid(*args, **kwargs)

    # def validate(self, data):
    #     task = data['task']
    #     profile_id = self.helper.id

    #     self._validate_status(data)
    #     self._validate_helper(task, profile_id)
    #     return super().validate(data)
