# Generated by Django 3.1.6 on 2021-04-26 10:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('userdetails', '0039_remove_transaction_tarif'),
        ('utils', '0016_city_country'),
        ('notifications', '0004_emailtypes_notificationtypes'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='NotificationTypes',
            new_name='NotificationType',
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('fullname_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='userdetails.userdetail')),
                ('notification_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='notifications.notificationtype')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_notifications', to='userdetails.userdetail')),
                ('service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='utils.service')),
            ],
        ),
    ]
