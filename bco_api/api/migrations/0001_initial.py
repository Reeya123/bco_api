# Generated by Django 3.2 on 2021-04-27 18:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='bco_draft',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.TextField()),
                ('schema', models.TextField()),
                ('state', models.TextField()),
                ('contents', models.JSONField()),
                ('object_class', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='bco_draft_meta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('n_objects', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='bco_publish',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.TextField()),
                ('schema', models.TextField()),
                ('state', models.TextField()),
                ('contents', models.JSONField()),
                ('object_class', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='bco_publish_meta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('n_objects', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='galaxy_draft',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.TextField()),
                ('schema', models.TextField()),
                ('state', models.TextField()),
                ('contents', models.JSONField()),
                ('object_class', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='galaxy_draft_meta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('n_objects', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='galaxy_publish',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.TextField()),
                ('schema', models.TextField()),
                ('state', models.TextField()),
                ('contents', models.JSONField()),
                ('object_class', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='galaxy_publish_meta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('n_objects', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='glygen_draft',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.TextField()),
                ('schema', models.TextField()),
                ('state', models.TextField()),
                ('contents', models.JSONField()),
                ('object_class', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='glygen_draft_meta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('n_objects', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='glygen_publish',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.TextField()),
                ('schema', models.TextField()),
                ('state', models.TextField()),
                ('contents', models.JSONField()),
                ('object_class', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='glygen_publish_meta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('n_objects', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='new_users',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('temp_identifier', models.TextField(max_length=100)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='oncomx_draft',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.TextField()),
                ('schema', models.TextField()),
                ('state', models.TextField()),
                ('contents', models.JSONField()),
                ('object_class', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='oncomx_draft_meta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('n_objects', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='oncomx_publish',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.TextField()),
                ('schema', models.TextField()),
                ('state', models.TextField()),
                ('contents', models.JSONField()),
                ('object_class', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='oncomx_publish_meta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('n_objects', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='prefix_groups',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prefix', models.CharField(max_length=5)),
                ('group_owner', models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='px_groups',
            fields=[
                ('prefix_groups_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='api.prefix_groups')),
            ],
            bases=('api.prefix_groups',),
        ),
        migrations.CreateModel(
            name='api_users_api_key',
            fields=[
                ('id', models.CharField(editable=False, max_length=100, primary_key=True, serialize=False, unique=True)),
                ('prefix', models.CharField(editable=False, max_length=8, unique=True)),
                ('hashed_key', models.CharField(editable=False, max_length=100)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('name', models.CharField(default=None, help_text='A free-form name for the API key. Need not be unique. 50 characters max.', max_length=50)),
                ('revoked', models.BooleanField(blank=True, default=False, help_text='If the API key is revoked, clients cannot use it anymore. (This cannot be undone.)')),
                ('expiry_date', models.DateTimeField(blank=True, help_text='Once API key expires, clients cannot use it anymore.', null=True, verbose_name='Expires')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='api_keys', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'API key',
                'verbose_name_plural': 'API keys',
                'ordering': ('-created',),
                'abstract': False,
            },
        ),
    ]
