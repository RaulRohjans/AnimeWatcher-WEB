# Generated by Django 3.2.1 on 2021-05-14 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Content', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='episode_class',
            name='mVideoFileLink',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='category_class',
            name='mDescription',
            field=models.TextField(max_length=750, null=True),
        ),
    ]
