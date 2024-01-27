import factory
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
    sender = SubFactory(ProfileFactory)
    recipient = SubFactory(ProfileFactory)
    sent_at = LazyFunction(timezone.now)

    @factory.post_generation
    def set_recipient(self, create, extracted, **kwargs):
        offer_helper = self.chat.assignment.offer.helper
        task_owner = self.chat.assignment.offer.task.owner

        if self.recipient not in (offer_helper, task_owner):
            self.recipient = (
                offer_helper if self.sender == task_owner else task_owner
            )

            if create:
                self.save()
