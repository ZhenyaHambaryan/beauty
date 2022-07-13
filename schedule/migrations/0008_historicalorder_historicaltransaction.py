# Generated by Django 3.1.6 on 2021-08-04 12:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        ('userdetails', '0042_remove_transaction_tarif'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('utils', '0018_aboutus'),
        ('schedule', '0007_order_go_home'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalTransaction',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('amount', models.FloatField(null=True)),
                ('payment_id', models.CharField(blank=True, max_length=1000, null=True)),
                ('date', models.DateTimeField(blank=True, editable=False)),
                ('status', models.CharField(blank=True, default='pending', max_length=255, null=True)),
                ('refunded_amount', models.FloatField(blank=True, default=0, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('client', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='userdetails.userdetail')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('master', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='userdetails.userdetail')),
                ('order', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='schedule.order')),
            ],
            options={
                'verbose_name': 'historical transaction',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalOrder',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('minutes', models.PositiveIntegerField(blank=True, null=True)),
                ('price', models.FloatField(blank=True, null=True)),
                ('go_home', models.BooleanField(default=False)),
                ('comment', models.CharField(blank=True, max_length=1000, null=True)),
                ('google_calendar_id', models.CharField(blank=True, max_length=500, null=True)),
                ('google_event_id', models.CharField(blank=True, max_length=500, null=True)),
                ('status', models.CharField(blank=True, max_length=255, null=True)),
                ('is_prepayed', models.BooleanField(default=False)),
                ('prepayed_price', models.FloatField(blank=True, null=True)),
                ('prepayed_status', models.CharField(blank=True, default='pending', max_length=255, null=True)),
                ('cancel_reason', models.CharField(blank=True, max_length=1000, null=True)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('payment_status', models.CharField(blank=True, default='pending', max_length=255, null=True)),
                ('payed_by_cache', models.BooleanField(default=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('master', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='userdetails.userdetail')),
                ('service', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='utils.service')),
                ('user', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='userdetails.userdetail')),
            ],
            options={
                'verbose_name': 'historical order',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]