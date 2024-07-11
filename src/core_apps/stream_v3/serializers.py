
from datetime import timedelta
import dateutil.parser

from rest_framework import serializers

from core_apps.stream_v3.models import VideoMetaData


class VideoMetaDataSerializer(serializers.ModelSerializer):
    """Serializer class for VideoMetaData class."""

    class Meta:
        model = VideoMetaData
        fields = ["original_video_title", "title", "description", "duration"]

     