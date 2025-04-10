# Generated by Django 4.2.2 on 2023-12-29 10:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("marketplace", "0009_offer"),
    ]

    operations = [
        migrations.AlterField(
            model_name="offer",
            name="status",
            field=models.CharField(
                choices=[("pending", "Pending"), ("accepted", "Accepted")],
                max_length=9,
            ),
        ),
    ]
