from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Profile, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = [
        'email',
        'first_name',
        'last_name',
        'email_verified',
    ]
    readonly_fields = ['email_verified']
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email',
                    'profile',
                    'password1',
                    'password2',
                ),
            },
        ),
    )

    fieldsets = (
        (
            None,
            {
                'fields': (
                    'email',
                    'password',
                    'profile',
                ),
            },
        ),
        (
            'Permissions',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                ),
            },
        ),
        (
            'Important dates',
            {
                'fields': ('last_login', 'date_joined'),
            },
        ),
    )

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        fields_wo_password = [field for field in fields if field != 'password']
        return fields_wo_password


class UserInline(admin.StackedInline):
    model = User
    can_delete = False
    verbose_name_plural = 'Users'

    fieldsets = (
        (
            None,
            {
                'fields': ('username', 'email', 'password'),
            },
        ),
        (
            'Permissions',
            {
                'fields': ('is_active', 'is_staff', 'is_superuser'),
            },
        ),
    )


@admin.register(Profile)
class CustomProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'name',
        'age_above_18',
        'agreed_with_conditions',
        'gender',
        'speaking_languages',
    ]

    inlines = [UserInline]
