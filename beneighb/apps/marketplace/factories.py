from factory import SubFactory
from factory.django import DjangoModelFactory

from apps.marketplace.models import Category, Subcategory


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category


class SubcategoryFactory(DjangoModelFactory):
    class Meta:
        model = Subcategory

    parent = SubFactory(CategoryFactory)
