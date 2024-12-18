# Generated by Django 4.2.16 on 2024-10-18 08:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("mynote", "0024_userdonloadkeyword_bookname"),
    ]

    operations = [
        migrations.CreateModel(
            name="NoteLisData",
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
                ("no", models.PositiveSmallIntegerField(verbose_name="書籍細項編號")),
                ("booklisurl", models.URLField(verbose_name="書籍細項連結")),
                (
                    "bookurl",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mynote.notedatas",
                        to_field="bookurl",
                        verbose_name="書本連結",
                    ),
                ),
            ],
            options={
                "db_table": "notelisinfo",
            },
        ),
    ]
