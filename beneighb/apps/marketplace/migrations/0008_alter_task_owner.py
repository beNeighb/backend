# Generated by Django 4.2.2 on 2023-11-20 18:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0007_remove_profile_subcategories_profile_services"),
        ("marketplace", "0007_task_owner"),
    ]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="users.profile"
            ),
        ),
    ]
