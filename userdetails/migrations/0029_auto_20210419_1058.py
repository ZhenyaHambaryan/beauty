# Generated by Django 3.1.6 on 2021-04-19 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userdetails', '0028_auto_20210416_0911'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='payment_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.DeleteModel(
            name='CreditCard',
        ),
    ]
