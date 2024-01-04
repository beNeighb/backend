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
    owner = models.ForeignKey('users.Profile', on_delete=models.CASCADE)
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


class Offer(models.Model):
    class StatusTypes(models.TextChoices):
        PENDING = ('pending', 'Pending')
        ACCEPTED = ('accepted', 'Accepted')

    task = models.ForeignKey('marketplace.Task', on_delete=models.CASCADE)
    helper = models.ForeignKey('users.Profile', on_delete=models.CASCADE)

    status = models.CharField(
        choices=StatusTypes.choices,
        max_length=9,
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return f'Offer-{self.id}|Task-{self.task.id}'


class Assignment(models.Model):
    class StatusTypes(models.TextChoices):
        PENDING = ('pending', 'Pending')
        ACCEPTED = ('accepted', 'Accepted')
        COMPLETED = ('completed', 'Completed')
        CANCELED = ('canceled', 'Canceled')

    offer = models.OneToOneField('marketplace.Offer', on_delete=models.CASCADE)
    status = models.CharField(
        choices=StatusTypes.choices,
        default=StatusTypes.PENDING,
        max_length=9,
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return f'Assignment-{self.id}|Offer-{self.offer.id}'
