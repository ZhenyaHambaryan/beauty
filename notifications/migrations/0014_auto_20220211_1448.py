# Generated by Django 3.1.6 on 2022-02-11 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0013_emailtypes_subject'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emailtypes',
            name='subject',
        ),
        migrations.AddField(
            model_name='emailtypes',
            name='subject_en',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='emailtypes',
            name='subject_fr',
            field=models.CharField(default='', max_length=255),
        ),
    ]
