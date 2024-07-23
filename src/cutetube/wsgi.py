"""
WSGI config for cutetube project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# TODO change settings to prod in production
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cutetube.settings.production")

application = get_wsgi_application()
