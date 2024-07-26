"""
URL configuration for cutetube project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
from django.urls import path, include
from django.conf import settings 
from django.conf.urls.static import static

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

# service documentation
doc_schema_view = get_schema_view(
    openapi.Info(
        title="CuteTube API",
        default_version="v1.0",
        description="API Endpoints for CuteTube VoD Platform Just Like YouTube",
        contact=openapi.Contact(email="connect.mahboobalam@gmail.com"),
        license=openapi.License(name="MIT Licence"),
    ),
    public=True,
    permission_classes=(AllowAny,),
)


urlpatterns = [
    path(f"{settings.ADMIN_URL}", admin.site.urls),
    
    # Doc URL 
    path("doc/", doc_schema_view.with_ui("redoc", cache_timeout=0)),
    
    # Version 01: Serve video by chunk
    path("app/", include("core_apps.stream.urls")),
    
    # Version 02: FFmpeg segmet serve and Segmentation done manually 
    path("app/v2/", include("core_apps.stream_v2.urls")),
    
    
    # Version 03: Celery Pipeline, S3, CDN, FFmpeg automated. 
    # Rest Framework API
    ### Stream_V3 APIs
    # Auth APIs
    path("api/v3/auth/", include("core_apps.accounts.urls")),
    # VoD V3 - Celery Pipeline, S3 and CDN
    path("api/v3/vod/", include("core_apps.stream_v3.urls")),
    
    
    # Version V4 - Celery Pipeline, S3, CDN and DRM (PlayReady Test Licence Server)
    path("api/v4/drm/vod/", include("core_apps.stream_v4.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_header = "CuteTube VoD API"
admin.site.site_title = "CuteTube Platform Admin Portal"
admin.site.index_title = "Welcome to CuteTube Platform API Portal"
