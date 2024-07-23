from django.contrib import admin

# Register your models here.


from core_apps.stream_v3.models import VideoMetaData


@admin.register(VideoMetaData)
class VideoMetaDataAdmin(admin.ModelAdmin):
    ''' Video Meta Data Model Admin Class.'''
    
    list_display = ["pkid", "id", "title", "slug", "created_at", "updated_at"]
    list_display_links = ["id", "title"]
