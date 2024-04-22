from django.db import migrations


def migrate_chat_models(apps, schema_editor):
    Chat = apps.get_model('chat', 'Chat')
    Assignment = apps.get_model('marketplace', 'Assignment')
    Offer = apps.get_model('marketplace', 'Offer')

    for chat in Chat.objects.all():
        # Check if the chat is associated with an Assignment
        if chat.assignment:
            # Get or create the associated Offer
            offer, _ = Offer.objects.get_or_create(assignment=chat.assignment)
            chat.offer = offer
            chat.save()
        else:
            # Create a new Chat with the Offer association
            offer = Offer.objects.create()
            chat.offer = offer
            chat.save()

class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_remove_chat_assignment_chat_offer'),
        ('marketplace', '0012_delete_chat'),
    ]

    operations = [
        migrations.RunPython(migrate_chat_models),
    ]
