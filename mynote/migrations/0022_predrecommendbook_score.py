# Generated by Django 4.2.16 on 2024-10-14 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mynote", "0021_predrecommendbook"),
    ]

    operations = [
        migrations.AddField(
            model_name="predrecommendbook",
            name="score",
            field=models.PositiveIntegerField(default=0, verbose_name="分數"),
            preserve_default=False,
        ),
    ]
