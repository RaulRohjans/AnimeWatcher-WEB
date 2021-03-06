# Generated by Django 3.2.5 on 2021-09-12 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Content', '0019_episode_class_mvcdn'),
    ]

    operations = [
        migrations.AddField(
            model_name='episode_class',
            name='mIsSpecial',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='anime_class',
            name='mNameEN',
            field=models.CharField(max_length=150, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='anime_class',
            name='mNameJP',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='episode_class',
            name='mNameEN',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='episode_class',
            name='mNameJP',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='submitanime_class',
            name='mAnimeName',
            field=models.CharField(max_length=150),
        ),
    ]
