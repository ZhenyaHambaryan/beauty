# Generated by Django 3.1.6 on 2021-03-26 13:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0012_auto_20210326_1742'),
        ('userdetails', '0009_auto_20210302_1036'),
    ]

    operations = [
        migrations.CreateModel(
            name='MasterTarifSubscribtion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expire_date', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('payed', models.BooleanField(default=False)),
                ('tarif', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='utils.tarif')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='master_subscribed_category', to='userdetails.userdetail')),
            ],
        ),
        migrations.CreateModel(
            name='TarifCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expire_date', models.DateTimeField()),
                ('tarif_subscribied', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscribied_category', to='userdetails.mastertarifsubscribtion')),
            ],
        ),
    ]
