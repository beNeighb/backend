from django.db import models


class Chat(models.Model):
    assignment = models.OneToOneField(
        'marketplace.Assignment',
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return f'Chat-{self.id}|Assignment-{self.assignment.id}'
