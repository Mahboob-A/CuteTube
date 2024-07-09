from django.urls import path 

from core_apps.stream_v2.views import (
    serve_dash_mpd,
    serve_dash_mpd_2,
    serve_dash_mpd_3,
    serve_dash_segment,
    serve_dash_segment_2,
    upload_to_s3,
)


# With dynamic directory (NOTE not working)
# urlpatterns = [
#     path(f"dash/<str:video_name>/manifest.mpd/", serve_dash_mpd, name="serve_dash_mpd"),
#     path(
#         "dash/<str:video_name>/<str:segment_name>/",
#         serve_dash_segment,
#         name="serve_dash_segment",
#     ),
# ]


#  serve_dash_mpd_2 and serve_dash_mpd_3
# serve_dash_segment_2
urlpatterns = [
    path(f"dash/manifest.mpd", serve_dash_mpd_2, name="serve_dash_mpd"),
    path(
        "dash/<str:segment_name>/",
        serve_dash_segment_2,
        name="serve_dash_segment",
    ),
    path("dash-2/upload-to-s3/", upload_to_s3, name="upload_to_s3"),
]
