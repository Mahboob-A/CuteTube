from django.urls import path

from core_apps.stream_v3.views import AllVideosAPI, StreamVideoVoDAPI, UploadVideoVoDAPI


urlpatterns = [
    
    # Get all videos. paginated resposne. 
    path("all/", AllVideosAPI.as_view(), name="all_videos_paginated_api"), 
    
    # Get S3 MPD url 
    path("meta-data/stream/<str:video_id>/", StreamVideoVoDAPI.as_view(), name="stream_video_metadata_api"),
    
    # Upload a video 
    path("initiate-task/upload/", UploadVideoVoDAPI.as_view(), name="uplaod_video_api"),
]
