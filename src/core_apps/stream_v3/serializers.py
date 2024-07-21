from datetime import timedelta
import dateutil.parser

from rest_framework import serializers

from core_apps.stream_v3.models import VideoMetaData


class VideoMetaDataSerializer(serializers.ModelSerializer):
    """Serializer class for VideoMetaData class."""

    class Meta:
        model = VideoMetaData
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
