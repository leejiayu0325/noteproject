# Generated by Django 4.2.16 on 2024-10-23 02:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("mynote", "0029_alter_creatuser_email_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="personalinformation",
            name="email",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                to="mynote.creatuser",
                to_field="email",
                verbose_name="使用者信箱",
            ),
        ),
    ]