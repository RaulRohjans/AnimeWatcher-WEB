# Generated by Django 3.2.5 on 2021-09-12 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Content', '0020_auto_20210912_1141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category_class',
            name='mCategoryName',
            field=models.CharField(max_length=100, primary_key=True, serialize=False, unique=True),
        ),
    ]
