# Generated by Django 3.1.6 on 2021-04-20 06:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0015_tarif_is_active'),
        ('userdetails', '0030_auto_20210420_1007'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='usercategory',
            unique_together={('user', 'category')},
        ),
    ]
