from datetime import timedelta
import dateutil.parser

from rest_framework import serializers

from core_apps.stream_v4.models import VideoMetaDataDRMV4


class VideoMetaDataDRMV4Serializer(serializers.ModelSerializer):
    """Serializer class for VideoMetaDataDRMV4 class."""

    class Meta:
        model = VideoMetaDataDRMV4
        fields = [
            "custom_video_title",
            "title",
            "description",
            "duration",
            "mp4_s3_mpd_url",
            "mov_s3_mpd_url",
            "mp4_gcore_cdn_mpd_url",
            "mov_gcore_cdn_mpd_url",
        ]
