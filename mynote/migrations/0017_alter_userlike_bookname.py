# Generated by Django 4.2.16 on 2024-10-09 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mynote", "0016_alter_notedatas_bookname_alter_userlike_bookname"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userlike",
            name="bookname",
            field=models.CharField(max_length=100, unique=True, verbose_name="書名"),
        ),
    ]
