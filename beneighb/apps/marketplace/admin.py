from django.contrib import admin

from .models import ServiceCategory, Service, Task


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

admin.site.register(
    Task,
    list_display=[
        'service',
        'id',
        'created_at',
        'datetime_known',
        'datetime_options',
        'event_type',
        'address',
        'price_offer',
    ],
)
