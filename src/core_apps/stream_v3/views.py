import os
import uuid

from django.http import JsonResponse
from django.conf import settings


from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, MultiPartParserError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from core_apps.stream_v3.models import VideoMetaData
from core_apps.stream_v3.serializers import VideoMetaDataSerializer
from core_apps.stream_v3.tasks import (
    process_and_save_video_local,
    upload_dash_segments_to_s3,
)


class UploadVideoAPI(APIView):
    """API to upload video in CuteTube platform by users."""

    parser_classes = [MultiPartParser]
    permission_classes = [AllowAny]  # TODO: change to is authenticated in production.

    def post(self, request, format=None):
        if "video" not in request.FILES:
            return Response(
                {"error": "No video file provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        (
            is_success,
            video_filename_without_extention,
            video_file_extention,
            local_video_path_with_extention,
            local_video_path_without_extention,
            db_data,
        ) = process_and_save_video_local(request=request)

        local_video_main_segments_dir_path = "/home/mehboob/poridhi-codes/cls-02-node-js-project/cutetube/src/vod-media/anime-village-lifestyle-segs"

        upload_dash_segments_to_s3.delay(
            local_video_main_segments_dir_path=local_video_main_segments_dir_path,
            video_filename_without_extention=video_filename_without_extention,
        )

        # if upload_success:
        #     print("uplaod success")
        #     print("\n: Failed segments to upload in if: ", failed_segments_to_upload)
        # else:
        #     print("\n: Failed segments to upload in else: ", failed_segments_to_upload)

        try:
            serializer = VideoMetaDataSerializer(data=db_data)

            if serializer.is_valid(raise_exception=True):
                video_metadata = serializer.save()
                return JsonResponse(
                    {
                        "data": {
                            "status": "Ok",
                            "video_id": video_metadata.id,
                            "video_name_without_extention": video_filename_without_extention,
                        }
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return JsonResponse(
                    {"data": {"status": "error", "detail": serializer.errors}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except ValidationError as e:
            error_dict = e.detail
            for key, value in error_dict.items():
                if key == "duration":
                    error_message = value[0]
                    data = {
                        "data": {
                            "status": "error",
                            "error_key": key,
                            "detail": str(error_message),
                        }
                    }
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
            return JsonResponse(
                {"data": {"status": "error", "detail": "Something error occurred."}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
