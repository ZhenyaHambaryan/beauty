# Generated by Django 3.1.6 on 2021-03-26 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0006_auto_20210302_1205'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='status',
            field=models.CharField(default='pending', max_length=255),
        ),
        migrations.AddField(
            model_name='postcomment',
            name='status',
            field=models.CharField(default='pending', max_length=255),
        ),
        migrations.AddField(
            model_name='review',
            name='status',
            field=models.CharField(default='pending', max_length=255),
        ),
    ]
