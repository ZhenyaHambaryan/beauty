# Generated by Django 3.1.6 on 2022-04-12 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0025_auto_20220118_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='general',
            name='stripe_key_for_master',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
