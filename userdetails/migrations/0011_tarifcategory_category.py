# Generated by Django 3.1.6 on 2021-03-26 13:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0012_auto_20210326_1742'),
        ('userdetails', '0010_mastertarifsubscribtion_tarifcategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='tarifcategory',
            name='category',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='utils.category'),
            preserve_default=False,
        ),
    ]
