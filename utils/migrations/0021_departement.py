# Generated by Django 3.1.6 on 2021-11-29 06:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0020_general'),
    ]

    operations = [
        migrations.CreateModel(
            name='Departement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title_en', models.CharField(blank=True, max_length=255, null=True)),
                ('title_fr', models.CharField(blank=True, max_length=255, null=True)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='utils.country')),
            ],
        ),
    ]
