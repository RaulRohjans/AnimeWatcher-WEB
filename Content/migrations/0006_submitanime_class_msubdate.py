# Generated by Django 3.2.1 on 2021-05-18 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Content', '0005_alter_subtitle_class_mlink'),
    ]

    operations = [
        migrations.AddField(
            model_name='submitanime_class',
            name='mSubDate',
            field=models.DateTimeField(null=True),
        ),
    ]