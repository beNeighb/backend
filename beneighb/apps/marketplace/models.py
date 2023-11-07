from django.db import models
from django.contrib.postgres.fields import ArrayField


class ServiceCategory(models.Model):
    name = models.CharField(
        max_length=150,
        blank=False,
    )
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Service Categories"


class Service(models.Model):
    name = models.CharField(
        max_length=150,
        blank=False,
    )
    description = models.TextField(null=True, blank=True)
    parent = models.ForeignKey('ServiceCategory', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Task(models.Model):
    class EventTypes(models.TextChoices):
        ONLINE = ('online', 'Online')
        OFFLINE = ('offline', 'Offline')

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    service = models.ForeignKey('Service', on_delete=models.PROTECT)
    datetime_known = models.BooleanField()
    datetime_options = ArrayField(
        models.DateTimeField(),
        size=3,
        default=list,
        blank=True,
    )
    event_type = models.CharField(
        choices=EventTypes.choices,
        max_length=7,
    )
    address = models.CharField(max_length=128, null=True, blank=True)
    price_offer = models.IntegerField()

    def __str__(self):
        return f'Task-{self.id} - {self.service.name}'
