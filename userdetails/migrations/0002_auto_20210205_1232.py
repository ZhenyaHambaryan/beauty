# Generated by Django 2.1 on 2021-02-05 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userdetails', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='confirmcode',
            name='email',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='confirmcode',
            name='phone_number',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
