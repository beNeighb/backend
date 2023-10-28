from django.db import models


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
