from django.urls import path

from core_apps.stream_v3.views import (
    AllVideosAPI,
    StreamVideoVoDAPI,
    UploadVideoVoDAPI,
    trigger_sentry_error,
)


urlpatterns = [
    
    # Get all videos. paginated resposne. 
    path("videos/all/", AllVideosAPI.as_view(), name="all_videos_paginated_api"), 
    
    # Get S3 MPD url 
    path("metadata/stream/<str:video_id>/", StreamVideoVoDAPI.as_view(), name="stream_video_metadata_api"),
    
    # Upload a video 
    path("initiate-task/upload/", UploadVideoVoDAPI.as_view(), name="uplaod_video_api"),
    
    
    # Sentry Error Trigger 
    path("sentry-error/", trigger_sentry_error, name="sentry_error_trigger"), 
]
