# Generated by Django 3.1.6 on 2021-04-26 09:08

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('userdetails', '0037_auto_20210426_1224'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdetail',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2021, 4, 26, 9, 8, 12, 381098, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
