# Generated by Django 3.1.6 on 2021-04-26 08:24

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0003_order_prepayed_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2021, 4, 26, 8, 24, 23, 838360, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
