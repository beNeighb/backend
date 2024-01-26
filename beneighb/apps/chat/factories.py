import factory
from django.utils import timezone

from factory import LazyAttribute, LazyFunction, SubFactory
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
            assignment = self.chat.assignment
            task_owner = assignment.offer.task.owner
            helper = assignment.offer.helper

            if self.sender == task_owner:
                self.recipient = helper
            elif self.sender == helper:
                self.recipient = task_owner

            if create:
                self.save()
