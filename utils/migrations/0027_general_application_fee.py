# Generated by Django 3.1.6 on 2022-06-21 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0026_general_stripe_key_for_master'),
    ]

    operations = [
        migrations.AddField(
            model_name='general',
            name='application_fee',
            field=models.IntegerField(default=10),
        ),
    ]
