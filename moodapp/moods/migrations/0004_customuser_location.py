# Generated by Django 4.2.17 on 2024-12-19 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moods', '0003_alter_usermood_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='location',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]