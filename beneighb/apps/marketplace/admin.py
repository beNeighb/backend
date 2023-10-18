from django.contrib import admin

from .models import Category, Subcategory


admin.site.register(
    Category,
    list_display=[
        'name',
        'id',
        'description',
    ],
)

admin.site.register(
    Subcategory,
    list_display=[
        'name',
        'id',
        'description',
        'parent',
    ],
)
