# Generated by Django 3.2.1 on 2021-05-18 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Content', '0004_episode_class_mselfhosted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subtitle_class',
            name='mLink',
            field=models.FileField(max_length=255, null=True, upload_to='subtitles/'),
        ),
    ]
