from copy import deepcopy
from django.contrib import admin, messages

from apps.users.models import Profile
from .models import Offer, ServiceCategory, Service, Task
from .serializers import OfferSerializer


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


class OfferAdminSerializer(OfferSerializer):
    """
    In OfferSerializer we get helper from context and set status to pending.
    Here we rely on data from admin form.
    """

    def __init__(self, *args, **kwargs):
        data = kwargs['data']
        self.helper = Profile.objects.get(id=data['helper'])

        # Do not want to call OfferSerializer.__init__ here
        super(OfferSerializer, self).__init__(*args, **kwargs)

    def is_valid(self, *args, **kwargs):
        # Do not want to call OfferSerializer.is_valid here
        return super(OfferSerializer, self).is_valid(*args, **kwargs)


class OfferAdmin(admin.ModelAdmin):
    model = Offer

    def save_model(self, request, obj, form, change):
        data_for_serializer = deepcopy(form.cleaned_data)
        data_for_serializer['helper'] = data_for_serializer['helper'].id
        data_for_serializer['task'] = data_for_serializer['task'].id

        serializer = OfferAdminSerializer(data=data_for_serializer)

        if serializer.is_valid():
            obj.save()
        else:
            error_messages = ', '.join(
                [
                    item
                    for sublist in serializer.errors.values()
                    for item in sublist
                ]
            )

            self.message_user(
                request,
                f'Validation error: {error_messages}',
                level=messages.ERROR,
            )


admin.site.register(Offer, OfferAdmin)
