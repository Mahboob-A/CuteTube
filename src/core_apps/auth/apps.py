from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _ 


class AuthAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core_apps.auth"
    verbose_name = _("CuteTube Auth")
    
