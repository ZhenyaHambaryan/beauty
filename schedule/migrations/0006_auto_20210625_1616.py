# Generated by Django 3.1.6 on 2021-06-25 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0005_order_cancel_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payed_by_cache',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_status',
            field=models.CharField(blank=True, default='pending', max_length=255, null=True),
        ),
    ]
