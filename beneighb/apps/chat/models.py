from django.db import models


class Chat(models.Model):
    offer = models.OneToOneField(
        'marketplace.Offer',
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return f'Chat-{self.id}|Offer-{self.offer.id}'


class Message(models.Model):
    # TODO: Do we need this field?
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    sender = models.ForeignKey(
        'users.Profile',
        on_delete=models.CASCADE,
        related_name='messages',
    )
    recipient = models.ForeignKey(
        'users.Profile',
        on_delete=models.CASCADE,
        related_name='received_messages',
    )

    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='messages',
    )

    sent_at = models.DateTimeField()
    read_at = models.DateTimeField(null=True, blank=True)

    text = models.TextField(max_length=300)

    def __str__(self):
        return f'Message-{self.id}|Chat-{self.id}|Offer-{self.chat.offer.id}'  # noqa
