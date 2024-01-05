from django.utils import timezone

from factory import LazyFunction, SubFactory
from factory.django import DjangoModelFactory

from apps.chat.models import Chat, Message
from apps.marketplace.factories import AssignmentFactory
from apps.users.factories import ProfileFactory


class ChatFactory(DjangoModelFactory):
    class Meta:
        model = Chat

    assignment = SubFactory(AssignmentFactory)


class MessageFactory(DjangoModelFactory):
    class Meta:
        model = Message

    chat = SubFactory(ChatFactory)
    author = SubFactory(ProfileFactory)
    sent_at = LazyFunction(timezone.now)
