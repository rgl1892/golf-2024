# Generated by Django 4.2.10 on 2024-03-25 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0016_alter_score_highlight_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='thumbnail',
            field=models.ImageField(blank=True, upload_to=''),
        ),
    ]
