# Generated by Django 2.1 on 2021-02-05 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0004_auto_20210205_0931'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimeType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_en', models.CharField(blank=True, max_length=255)),
                ('name_fr', models.CharField(blank=True, max_length=255)),
            ],
        ),
    ]