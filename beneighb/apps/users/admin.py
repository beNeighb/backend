from django.contrib import admin
from .models import User, Profile

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

admin.site.register(
    Profile,
    list_display=[
        'name',
        'age_above_18',
        'agreed_with_conditions',
        'gender',
        'speaking_languages',
    ],
)
