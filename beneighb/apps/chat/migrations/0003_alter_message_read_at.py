# Generated by Django 4.2.2 on 2024-01-04 14:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0002_message"),
    ]

    operations = [
        migrations.AlterField(
            model_name="message",
            name="read_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
