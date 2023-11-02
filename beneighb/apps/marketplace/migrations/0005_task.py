# Generated by Django 4.2.2 on 2023-11-02 07:13

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("marketplace", "0004_alter_servicecategory_options"),
    ]

    operations = [
        migrations.CreateModel(
            name="Task",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("datetime_known", models.BooleanField()),
                (
                    "datetime_options",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.DateTimeField(), size=3
                    ),
                ),
                (
                    "event_type",
                    models.CharField(
                        choices=[("online", "Online"), ("offline", "Offline")],
                        max_length=7,
                    ),
                ),
                (
                    "address",
                    models.CharField(
                        choices=[("online", "Online"), ("offline", "Offline")],
                        max_length=128,
                    ),
                ),
                ("price_offer", models.IntegerField()),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="marketplace.service",
                    ),
                ),
            ],
        ),
    ]
