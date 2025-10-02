import os
from celery import Celery

# Set default Django settings module for 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dropship_bot.settings')

app = Celery('dropship_bot')

# Read config from Django settings, namespace all CELERY_* variables.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in installed apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):  # pragma: no cover
    print(f'Request: {self.request!r}')
