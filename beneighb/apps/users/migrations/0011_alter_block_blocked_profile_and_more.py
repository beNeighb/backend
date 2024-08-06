# Generated by Django 4.2.2 on 2024-08-06 12:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0010_block'),
    ]

    operations = [
        migrations.AlterField(
            model_name='block',
            name='blocked_profile',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='blocked_profiles',
                to='users.profile',
            ),
        ),
        migrations.AlterField(
            model_name='block',
            name='blocking_profile',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='blocking_profiles',
                to='users.profile',
            ),
        ),
    ]
