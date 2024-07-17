import os 

from celery import Celery

from django.conf import settings

# TODO change to .prod in prodction environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cutetube.settings.dev")

app = Celery('cutetube')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
