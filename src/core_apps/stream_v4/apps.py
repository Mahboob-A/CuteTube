from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _ 


class StreamV4Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core_apps.stream_v4"
    verbose_name = -("Stream V4 - DRM Version")
