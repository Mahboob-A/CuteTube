from django.contrib import admin

# Register your models here.


from core_apps.stream_v4.models import VideoMetaDataDRMV4


@admin.register(VideoMetaDataDRMV4)
class VideoMetaDataDRMV4Admin(admin.ModelAdmin):
    """Video Meta Data DRM V4 Model Admin Class."""

    list_display = ["pkid", "id", "title", "slug", "created_at", "updated_at"]
    list_display_links = ["id", "title"]
