# Generated by Django 3.2.1 on 2021-05-19 22:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Content', '0007_comment_class'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment_class',
            name='mRepliedUser',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
