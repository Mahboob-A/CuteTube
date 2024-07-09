from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class StreamV2Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core_apps.stream_v2"
    verbose_name = "Stream V2"
    verbose_name_plural = "Streams V2"
