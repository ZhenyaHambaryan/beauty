# Generated by Django 3.1.6 on 2021-03-02 07:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('userdetails', '0009_auto_20210302_1036'),
        ('timeline', '0002_auto_20210302_0910'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(blank=True, null=True)),
                ('reply', models.TextField(blank=True, null=True)),
                ('rating', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='written_reviews', to='userdetails.userdetail')),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='my_reviews', to='userdetails.userdetail')),
            ],
        ),
    ]
