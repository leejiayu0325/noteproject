# Generated by Django 4.2.16 on 2024-10-24 00:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mynote", "0035_remove_notedatas_bookstate"),
    ]

    operations = [
        migrations.AddField(
            model_name="notedatas",
            name="bookstate",
            field=models.BooleanField(default=False, verbose_name="完本記錄"),
            preserve_default=False,
        ),
    ]