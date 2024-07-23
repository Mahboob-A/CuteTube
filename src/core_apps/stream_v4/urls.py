from django.urls import path

from core_apps.stream_v4.views import (
    AllVideosAPIDRMV4,
    StreamVideoVoDDRMV4API,
    UploadVideoVoDDRMV4API,
)


urlpatterns = [
    # Get all videos. paginated resposne.
    path("videos/all/", AllVideosAPIDRMV4.as_view(), name="all_videos_paginated_drm_api"),
    # Get S3 MPD url
    path(
        "metadata/stream/<str:video_id>/",
        StreamVideoVoDDRMV4API.as_view(),
        name="stream_video_metadata_drm_api",
    ),
    # Upload a video
    path(
        "initiate-task/upload/",
        UploadVideoVoDDRMV4API.as_view(),
        name="uplaod_video_drm_api",
    ),
]
