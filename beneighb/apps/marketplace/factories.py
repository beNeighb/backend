from factory import SubFactory
from factory.django import DjangoModelFactory

from apps.marketplace.models import ServiceCategory, Service


class ServiceCategoryFactory(DjangoModelFactory):
    class Meta:
        model = ServiceCategory


class ServiceFactory(DjangoModelFactory):
    class Meta:
        model = Service

    parent = SubFactory(ServiceCategoryFactory)
