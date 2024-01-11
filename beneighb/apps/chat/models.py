from django.db import models


class Chat(models.Model):
    assignment = models.OneToOneField(
        'marketplace.Assignment',
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return f'Chat-{self.id}|Assignment-{self.assignment.id}'


class Message(models.Model):
    # TODO: Do we need this field?
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    author = models.ForeignKey(
        'users.Profile',
        on_delete=models.CASCADE,
        related_name='messages',
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
        return f'Message-{self.id}|Chat-{self.id}|Offer-{self.chat.assignment.offer.id}'  # noqa
