# Generated by Django 4.2.16 on 2024-10-13 12:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("mynote", "0020_userlike_unique_user_bookurl"),
    ]

    operations = [
        migrations.CreateModel(
            name="PredRecommendBook",
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
                "db_table": "pred_book",
            },
        ),
    ]