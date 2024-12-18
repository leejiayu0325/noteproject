# Generated by Django 4.2.16 on 2024-10-24 00:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mynote", "0033_alter_donloadbookanduser_user_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="notedatas",
            name="bookstate",
            field=models.BooleanField(default=False, verbose_name="完本記錄"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="creatuser",
            name="password",
            field=models.CharField(max_length=128),
        ),
    ]
