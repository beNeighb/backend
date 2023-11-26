from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Profile, User


class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'email_verified']
    readonly_fields = ['email_verified']
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email',
                    'password1',
                    'password2',
                ),
            },
        ),
    )

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)

        # Exclude the password field from the list of fields
        fields = [field for field in fields if field != 'password']

        return fields


admin.site.register(User, CustomUserAdmin)


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
