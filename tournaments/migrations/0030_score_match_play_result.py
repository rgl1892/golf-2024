# Generated by Django 5.0.2 on 2024-08-08 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0029_carouselimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='score',
            name='match_play_result',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
