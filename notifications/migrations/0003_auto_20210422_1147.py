# Generated by Django 3.1.6 on 2021-04-22 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_auto_20210414_1526'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheduledemail',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='schedulednotification',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
