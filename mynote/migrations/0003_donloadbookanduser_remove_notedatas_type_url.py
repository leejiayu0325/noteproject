# Generated by Django 4.2.16 on 2024-09-30 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mynote", "0002_bookandurl"),
    ]

    operations = [
        migrations.CreateModel(
            name="DonloadBookandUser",
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
                ("user", models.CharField(max_length=50)),
                ("bookname", models.CharField(max_length=100, verbose_name="書名")),
            ],
            options={
                "db_table": "userdownload",
            },
        ),
        migrations.RemoveField(
            model_name="notedatas",
            name="type_url",
        ),
    ]
