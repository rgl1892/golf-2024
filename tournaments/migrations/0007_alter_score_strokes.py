# Generated by Django 4.2.10 on 2024-02-26 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0006_score_handicap'),
    ]

    operations = [
        migrations.AlterField(
            model_name='score',
            name='strokes',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
