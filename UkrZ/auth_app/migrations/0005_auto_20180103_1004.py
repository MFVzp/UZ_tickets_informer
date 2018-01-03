# Generated by Django 2.0 on 2018-01-03 10:04

import auth_app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0004_myuser_tel_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='viber_id',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='myuser',
            name='viber_secret_message',
            field=models.CharField(default=auth_app.models.get_random_code, max_length=32),
        ),
    ]