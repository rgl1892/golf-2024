# Generated by Django 4.2.10 on 2024-03-21 16:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0013_score_highlight_link'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Highlight',
        ),
    ]
