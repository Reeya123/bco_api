# Generated by Django 3.2.13 on 2024-03-07 21:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_rename_prefixes_prefix'),
    ]

    operations = [
        migrations.DeleteModel(
            name='new_users',
        ),
    ]
