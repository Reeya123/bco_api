# Generated by Django 3.2.13 on 2024-03-07 21:53

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('temp_identifier', models.TextField(max_length=100)),
                ('token', models.TextField(blank=True, null=True)),
                ('hostname', models.TextField(blank=True, null=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
