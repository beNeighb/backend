from factory import SubFactory
from factory.django import DjangoModelFactory

from apps.marketplace.factories import AssignmentFactory
from apps.chat.models import Chat


class ChatFactory(DjangoModelFactory):
    class Meta:
        model = Chat

    assignment = SubFactory(AssignmentFactory)
