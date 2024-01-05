from rest_framework import serializers
from apps.chat.models import Message


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
        """
        If message is already read,
        serilizer will return read_at value without updating it.
        """
        if instance.read_at is None:
            instance.read_at = validated_data.get('read_at', instance.read_at)
            instance.save()

        return instance
