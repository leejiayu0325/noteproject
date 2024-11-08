# Generated by Django 4.2.16 on 2024-10-20 04:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mynote", "0026_notepath"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="donloadbookanduser",
            constraint=models.UniqueConstraint(
                fields=("user", "bookurl"), name="unique_dowl_user_bookurl"
            ),
        ),
    ]
