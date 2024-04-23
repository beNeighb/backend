import factory
from django.utils import timezone

from factory import LazyFunction, SubFactory
from factory.django import DjangoModelFactory

from apps.chat.models import Chat, Message
from apps.users.factories import ProfileFactory


class ChatFactory(DjangoModelFactory):
    class Meta:
        model = Chat

    @classmethod
    def create(cls, offer=None, **kwargs):
        if offer is None:
            from apps.marketplace.factories import OfferFactory
            offer = OfferFactory()
        else:
            kwargs['offer_id'] = offer.id

        if not hasattr(offer, 'chat'):
            chat = super().create(offer=offer)
        else:
            chat = offer.chat

        return chat


class MessageFactory(DjangoModelFactory):
    class Meta:
        model = Message

    sender = SubFactory(ProfileFactory)
    recipient = SubFactory(ProfileFactory)
    sent_at = LazyFunction(timezone.now)

    @classmethod
    def create(cls, chat=None, sender=None, *args, **kwargs):
        if not chat:
            chat = ChatFactory.create(*args, **kwargs)
            if sender:
                message = super().create(sender=sender, *args, **kwargs)
            else:
                message = super().create(chat=chat, *args, **kwargs)
        else:
            message = super().create(chat=chat, sender=sender, *args, **kwargs)

        return message


    @factory.post_generation
    def set_recipient(self, create, extracted, **kwargs):
        offer_helper = self.chat.offer.helper
        task_owner = self.chat.offer.task.owner

        if self.recipient not in (offer_helper, task_owner):
            self.recipient = (
                offer_helper if self.sender == task_owner else task_owner
            )

            if create:
                self.save()
