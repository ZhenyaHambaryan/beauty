# Generated by Django 3.1.6 on 2022-01-27 05:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userdetails', '0045_userdetail_is_popular'),
    ]

    operations = [
        migrations.AlterField(
            model_name='masterservice',
            name='go_home_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=25, null=True),
        ),
        migrations.AlterField(
            model_name='masterservice',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=25, null=True),
        ),
    ]
