from django.db import migrations, models
import uuid
import django.utils.timezone
from django.core.validators import MinValueValidator


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScrapeJob',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ('task_id', models.CharField(max_length=255, null=True, blank=True)),
                ('query', models.CharField(max_length=300)),
                ('source', models.CharField(max_length=100)),
                ('status', models.CharField(max_length=20, choices=[('PENDING', 'Pending'), ('STARTED', 'Started'), ('SUCCESS', 'Success'), ('FAILURE', 'Failure'), ('REVOKED', 'Revoked')], default='PENDING')),
                ('requested_pages', models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])),
                ('returned_items', models.PositiveIntegerField(default=0)),
                ('created_items', models.PositiveIntegerField(default=0)),
                ('progress', models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text='Porcentaje 0-100')),
                ('error', models.TextField(null=True, blank=True)),
                ('meta', models.JSONField(default=dict, blank=True)),
                ('started_at', models.DateTimeField(null=True, blank=True)),
                ('finished_at', models.DateTimeField(null=True, blank=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now))
            ],
            options={
                'verbose_name': 'Scrape Job',
                'verbose_name_plural': 'Scrape Jobs',
                'ordering': ['-created_at']
            }
        )
    ]
