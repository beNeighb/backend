from django.contrib import admin
from .models import User

# Register your models here.
admin.site.register(
    User,
    list_display=[
        'email',
        'first_name',
        'last_name',
        'email_verified',
    ],
    read_only=['email_verified'],
)
