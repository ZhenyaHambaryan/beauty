# Generated by Django 3.1.6 on 2021-05-31 12:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('userdetails', '0042_remove_transaction_tarif'),
        ('timeline', '0015_auto_20210426_1224'),
    ]

    operations = [
        migrations.CreateModel(
            name='HidePost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_hide', to='timeline.post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_hide_posts', to='userdetails.userdetail')),
            ],
            options={
                'unique_together': {('user', 'post')},
            },
        ),
    ]
