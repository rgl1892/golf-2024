# Generated by Django 4.2.10 on 2024-03-21 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0012_video_highlight'),
    ]

    operations = [
        migrations.AddField(
            model_name='score',
            name='highlight_link',
            field=models.ManyToManyField(to='tournaments.video'),
        ),
    ]