# Generated by Django 3.1.6 on 2021-04-01 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0014_auto_20210401_1143'),
    ]

    operations = [
        migrations.AddField(
            model_name='tarif',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
