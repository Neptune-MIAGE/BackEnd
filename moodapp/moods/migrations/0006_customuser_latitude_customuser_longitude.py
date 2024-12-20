# Generated by Django 4.2.17 on 2024-12-19 22:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moods', '0005_usermood_weather_condition'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
