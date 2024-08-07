"""
ASGI config for cutetube project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# TODO change settings to prod in production
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cutetube.settings.production")

application = get_asgi_application()
