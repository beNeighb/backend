from django.contrib import admin

from .models import Chat, Message


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_offer_helper', 'get_task_owner', 'created_at']

    def get_task_owner(self, obj):
        if obj.assignment:
            return obj.assignment.offer.task.owner

    def get_offer_helper(self, obj):
        if obj.assignment:
            return obj.assignment.offer.helper

    get_task_owner.short_description = 'Task owner'
    get_offer_helper.short_description = 'Offer helper'


admin.site.register(
    Message,
    list_display=[
        'id',
        'sender',
        'recipient',
        'chat',
        'sent_at',
        'read_at',
        'text',
    ],
)
