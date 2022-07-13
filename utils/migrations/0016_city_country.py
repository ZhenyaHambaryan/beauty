# Generated by Django 3.1.6 on 2021-04-23 06:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0015_tarif_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title_en', models.CharField(blank=True, max_length=255, null=True)),
                ('title_fr', models.CharField(blank=True, max_length=255, null=True)),
                ('code', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title_en', models.CharField(blank=True, max_length=255, null=True)),
                ('title_fr', models.CharField(blank=True, max_length=255, null=True)),
                ('logitude', models.CharField(blank=True, max_length=255, null=True)),
                ('latitude', models.CharField(blank=True, max_length=255, null=True)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='utils.country')),
            ],
        ),
    ]
