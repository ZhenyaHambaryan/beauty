# Generated by Django 3.1.6 on 2022-02-26 08:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userdetails', '0046_auto_20220127_0939'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userdetail',
            name='push_token',
        ),
    ]