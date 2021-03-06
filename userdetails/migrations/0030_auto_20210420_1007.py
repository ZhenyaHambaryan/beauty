# Generated by Django 3.1.6 on 2021-04-20 06:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0015_tarif_is_active'),
        ('userdetails', '0029_auto_20210419_1058'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='utils.category')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userdetails.userdetail')),
            ],
        ),
        migrations.DeleteModel(
            name='TarifCategory',
        ),
    ]
