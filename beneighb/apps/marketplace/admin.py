from django.contrib import admin

from .models import ServiceCategory, Service


admin.site.register(
    ServiceCategory,
    list_display=[
        'name',
        'id',
        'description',
    ],
)

admin.site.register(
    Service,
    list_display=[
        'name',
        'id',
        'description',
        'parent',
    ],
)
