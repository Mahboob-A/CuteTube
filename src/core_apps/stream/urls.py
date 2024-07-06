from django.urls import path

from core_apps.stream.views import stream_video

urlpatterns = [
    path("stream/", stream_video, name="api_stream_video"),
]
