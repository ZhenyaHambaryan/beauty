# Generated by Django 3.1.6 on 2021-04-08 11:55

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ('userdetails', '0017_remove_transaction_tarif'),
    ]
    operations = [
        migrations.AddField(
            model_name='tarifcategory',
            name='subscribied_tarif',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, related_name='subscribied_category', to='userdetails.mastertarifsubscribtion'),
            preserve_default=False,
        ),
    ]
