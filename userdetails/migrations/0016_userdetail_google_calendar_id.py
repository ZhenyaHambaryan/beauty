# Generated by Django 3.1.6 on 2021-04-03 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userdetails', '0015_remove_transaction_tarif'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdetail',
            name='google_calendar_id',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
