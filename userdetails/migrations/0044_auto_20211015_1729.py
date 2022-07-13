# Generated by Django 3.1.6 on 2021-10-15 13:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0019_aboutus_image'),
        ('userdetails', '0043_favoritemasters'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mastertarifsubscribtion',
            name='tarif',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tarif_users', to='utils.tarif'),
        ),
    ]