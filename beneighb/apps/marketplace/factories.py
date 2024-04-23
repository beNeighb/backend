from factory import SubFactory, LazyAttribute
from factory.django import DjangoModelFactory

from apps.chat.factories import ChatFactory
from apps.marketplace.models import (
    Assignment,
    Offer,
    ServiceCategory,
    Service,
    Task,
)
from apps.users.factories import ProfileFactory


class ServiceCategoryFactory(DjangoModelFactory):
    class Meta:
        model = ServiceCategory


class ServiceFactory(DjangoModelFactory):
    class Meta:
        model = Service

    parent = SubFactory(ServiceCategoryFactory)


class TaskFactory(DjangoModelFactory):
    class Meta:
        model = Task

    datetime_known = True
    event_type = 'online'
    price_offer = 100
    service = SubFactory(ServiceFactory)
    owner = SubFactory(ProfileFactory)


class AssignmentFactory(DjangoModelFactory):
    class Meta:
        model = Assignment


class OfferFactory(DjangoModelFactory):
    class Meta:
        model = Offer

    task = SubFactory(TaskFactory)
    helper = SubFactory(ProfileFactory)
    status = 'pending'

    @classmethod
    def create(cls, is_with_assignment=False, **kwargs):
        offer = super().create(**kwargs)
        ChatFactory(offer=offer)
        if is_with_assignment:
            AssignmentFactory(offer=offer)
        return offer
