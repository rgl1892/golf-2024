# Generated by Django 4.2.4 on 2024-02-09 18:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0002_remove_holiday_resort_visit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hole',
            name='hole_name',
        ),
    ]