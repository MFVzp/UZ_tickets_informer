# Generated by Django 2.0 on 2018-01-03 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchinginfo',
            name='date_dep_in_datetime_format',
            field=models.DateField(null=True),
        ),
    ]
