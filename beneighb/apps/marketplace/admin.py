from django.contrib import admin

from .models import Category, SubCategory


admin.site.register(
    Category,
    list_display=[
        'name',
        'description',
    ],
)

admin.site.register(
    SubCategory,
    list_display=[
        'parent',
        'name',
        'description',
    ],
)
