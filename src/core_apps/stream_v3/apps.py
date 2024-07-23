from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _ 

class StreamV3Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core_apps.stream_v3"
    verbose_name = _("Stream V3 - FFmpeg with CDN")
    verbose_name_plural = _("Streams V3")
    
