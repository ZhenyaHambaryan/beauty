# Generated by Django 3.1.6 on 2021-04-09 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0011_review_google_event_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='google_event_id',
            field=models.CharField(blank=True, default='pending', max_length=255, null=True),
        ),
    ]
