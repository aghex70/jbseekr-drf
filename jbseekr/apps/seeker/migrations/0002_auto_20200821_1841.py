# Generated by Django 3.1 on 2020-08-21 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seeker', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='role',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
