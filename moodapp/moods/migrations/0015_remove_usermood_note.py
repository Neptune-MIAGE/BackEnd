# Generated by Django 4.2.17 on 2025-01-19 15:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('moods', '0014_moodranking'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usermood',
            name='note',
        ),
    ]
