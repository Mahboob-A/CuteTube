from django.urls import path

from core_apps.stream_v3.views import UploadVideoAPI


urlpatterns = [
    path("initiate-task/upload-video/", UploadVideoAPI.as_view(), name="uplaod_video")
]
