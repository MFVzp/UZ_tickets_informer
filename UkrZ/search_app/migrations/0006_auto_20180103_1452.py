# Generated by Django 2.0 on 2018-01-03 14:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search_app', '0005_auto_20180103_1449'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='searchinginfo',
            options={'ordering': ['date_dep_in_datetime_format']},
        ),
    ]
