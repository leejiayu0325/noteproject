# Generated by Django 4.2.16 on 2024-10-08 16:20

from django.db import migrations, models
import mynote.models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ("mynote", "0012_alter_personalinformation_email"),
    ]

    operations = [
        migrations.CreateModel(
            name="Profile",
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
                ("name", models.CharField(max_length=50)),
                (
                    "picture",
                    models.ImageField(upload_to=mynote.models.user_directory_path),
                ),
            ],
            options={
                "db_table": "profile",
            },
        ),
        migrations.AlterField(
            model_name="personalinformation",
            name="phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True, max_length=128, null=True, region=None
            ),
        ),
    ]
