# Generated by Django 4.2.17 on 2024-12-19 22:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('moods', '0006_customuser_latitude_customuser_longitude'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='longitude',
        ),
        migrations.RemoveField(
            model_name='usermood',
            name='weather_condition',
        ),
    ]
