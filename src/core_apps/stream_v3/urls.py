from django.urls import path

from core_apps.stream_v3.views import StreamVideoVoDAPI, UploadVideoVoDAPI


urlpatterns = [
    path("meta-data/stream/<str:video_id>/", StreamVideoVoDAPI.as_view(), name="stream_video_metadata_api"),
    path("initiate-task/upload/", UploadVideoVoDAPI.as_view(), name="uplaod_video_api"),
]
