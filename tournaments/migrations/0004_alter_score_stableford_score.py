# Generated by Django 5.0.2 on 2024-02-10 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0003_remove_hole_hole_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='score',
            name='stableford_score',
            field=models.IntegerField(blank=True),
        ),
    ]