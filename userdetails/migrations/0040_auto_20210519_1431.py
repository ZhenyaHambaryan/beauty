# Generated by Django 3.1.6 on 2021-05-19 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userdetails', '0039_remove_transaction_tarif'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdetail',
            name='push_token',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
