# Generated by Django 3.1.6 on 2021-06-02 11:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0007_auto_20210602_1147'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='scheduled_notif',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sch_notifs', to='notifications.schedulednotification'),
            preserve_default=False,
        ),
    ]
