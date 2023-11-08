from factory import SubFactory
from factory.django import DjangoModelFactory

from apps.marketplace.models import ServiceCategory, Service, Task


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
