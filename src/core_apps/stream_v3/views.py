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
    transcode_video_to_mov_or_mp4,
    dash_segment_video,
    process_and_save_video_local,
    upload_dash_segments_to_s3,
    cleanup_local_files_and_segments,
)


class UploadVideoAPI(APIView):
    """API to upload video in CuteTube platform by users."""

    parser_classes = [MultiPartParser]
    permission_classes = [AllowAny]  # TODO: change to is authenticated in production.

    def transcode_and_segment_transcoded_video(
        self,
        video_file_extention,
        video_filename_without_extention,
        local_video_path_with_extention,
        local_video_path_without_extention,
    ):
        """Wrapper Method to Transcode the original video file to mov or mp4 depending upon the original vidoe file format."""

        # Transcode the video to mp4 or mov depending upon the original video format.
        # If the original vidoe is mp4, then convert into mov and vice-versa, and then segment the transcoded video.
        # Once the video is transcoded, segment it. The original video will be segmented after the transcoded video.

        # The local temporary manifest.mpd file path is: BASE_DIR/local-vod-segments-temp/UUID__rain-bg-video/mov/manifest.mpd
        # The S3 manifest.mpd file path is: vod-media/UUID__rain-calm-video/extention/manifest.mpd
        # EX: f"https://{s3_bucket_name}.s3.amazonaws.com/vod-media/{video_name}/extention/manifest.mpd"

        # Transcode the video.
        if video_file_extention == ".mp4":

            mov_video_file_path_with_extention = os.path.join(
                local_video_path_without_extention, ".mov"
            )

            # transcode to mov
            transcode_video_to_mov_or_mp4.delay(
                local_video_path_with_extention=local_video_path_with_extention,
                local_path_to_transcoded_video_with_extention=mov_video_file_path_with_extention,  # transcoded and original video will be stored in same dir, but the extention name will differ
            )

            # Dir to store segments of transcoded video.
            #  BASE_DIR/vod-media/local-vod-segments-temp/uuid__rain-bg-video/mov
            mov_segment_files_output_dir = f"{settings.DASH_LOCAL_VOD_SEGMENT_DIR_ROOT}/{video_filename_without_extention}/mov"

            os.makedirs(mov_segment_files_output_dir, exist_ok=True)

            # segment the mov file
            dash_segment_video.delay(
                local_video_path_with_extention=mov_video_file_path_with_extention,
                segment_files_output_dir=mov_segment_files_output_dir,
            )

        elif video_file_extention == ".mov":

            mp4_video_file_path_with_extention = os.path.join(
                local_video_path_without_extention, ".mp4"
            )

            transcode_video_to_mov_or_mp4.delay(
                local_video_path_with_extention=local_video_path_with_extention,
                local_path_to_transcoded_video_with_extention=mp4_video_file_path_with_extention,
            )

            # BASE_DIR/local-vod-segments-temp/UUID__rain-bg-video/mp4
            mp4_segment_files_output_dir = f"{settings.DASH_LOCAL_VOD_SEGMENT_DIR_ROOT}/{video_filename_without_extention}/mp4"

            os.makedirs(mov_segment_files_output_dir, exist_ok=True)

            dash_segment_video.delay(
                local_video_path_with_extention=mp4_video_file_path_with_extention,
                segment_files_output_dir=mp4_segment_files_output_dir,
            )

    def segment_original_video(
        self,
        video_file_extention,
        video_filename_without_extention,
        local_video_path_with_extention,
        local_video_path_without_extention,
    ):
        """Wrapper Method to Segment the original video file."""

        # The local temporary manifest.mpd file path is: BASE_DIR/local-vod-segments-temp/UUID__rain-bg-video/mov/manifest.mpd
        # The S3 manifest.mpd file path is: vod-media/UUID__rain-calm-video/extention/manifest.mpd
        # EX: f"https://{s3_bucket_name}.s3.amazonaws.com/vod-media/{video_name}/extention/manifest.mpd"

        # Segment the original video
        if video_file_extention == ".mp4":

            # BASE_DIR/local-vod-segments-temp/UUID__rain-bg-video/mp4
            mp4_segment_files_output_dir = f"{settings.DASH_LOCAL_VOD_SEGMENT_DIR_ROOT}/{video_filename_without_extention}/mp4"

            os.makedirs(mp4_segment_files_output_dir, exist_ok=True)

            dash_segment_video.delay(
                local_video_path_with_extention=local_video_path_with_extention,
                segment_files_output_dir=mp4_segment_files_output_dir,
            )

        elif video_file_extention == ".mov":

            # BASE_DIR/local-vod-segments-temp/UUID__rain-bg-video/mov
            mov_segment_files_output_dir = f"{settings.DASH_LOCAL_VOD_SEGMENT_DIR_ROOT}/{video_filename_without_extention}/mov"

            os.makedirs(mov_segment_files_output_dir, exist_ok=True)

            dash_segment_video.delay(
                local_video_path_with_extention=local_video_path_with_extention,
                segment_files_output_dir=mov_segment_files_output_dir,
            )

    def upload_segments_s3(
        self,
        video_file_extention,
        video_filename_without_extention,
    ):
        """Wrapper Method to upload the segmented files of mp4 and mov container format to S3."""

        # BASE_DIR/local-vod-segments-temp/UUID__rain-bg-video/mov
        # mov_segment_files_output_dir = f"{settings.DASH_LOCAL_VOD_SEGMENT_DIR_ROOT}/{video_filename_without_extention}/mov"

        # # Upload mov Video Segments to S3
        # upload_dash_segments_to_s3.delay(
        #     video_file_extention=video_file_extention,
        #     local_video_main_segments_dir_path=mov_segment_files_output_dir,
        #     video_filename_without_extention=video_filename_without_extention,
        # )

        #  BASE_DIR/local-vod-segments-temp/UUID__rain-bg-video/mp4
        mp4_segment_files_output_dir = f"{settings.DASH_LOCAL_VOD_SEGMENT_DIR_ROOT}/{video_filename_without_extention}/mp4"

        # Upload mp4 Video Segments to S3
        upload_dash_segments_to_s3.delay(
            video_file_extention=video_file_extention,
            local_video_main_segments_dir_path=mp4_segment_files_output_dir,
            video_filename_without_extention=video_filename_without_extention,
        )
        
    # def cleanup_local_filesand_segments_method()

    def post(self, request, format=None):
        """/upload URL.

        The API takes a video file, saves in local storage, creates some celery tasks, saves the video metadata into Database, and response.

        Workflow:
        
            1. Save video to local storage.
            
            2. Independent Celery Tasks: (The API doesn't wait for the below tasks to be completed to response)

                i. transcode original video to mov or mp4
                ii. segment the transcoded video (resolutions: 360, 480, 720, 1080)

                iii. segment the original video. (resolutions: 360, 480, 720, 1080)
                iv. upload the both segmented videos formats to S3.
                
                v. delete the transcoded files. 
                vi. delete the local file. 
            
            3. Save metadata in DB and response. 
        """

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

        # local_video_main_segments_dir_path = "/home/mehboob/poridhi-codes/cls-02-node-js-project/cutetube/src/vod-media/anime-village-lifestyle-segs"

        # Task 01: Transcode and Segment to other (mov or mp4) format.
        # self.transcode_and_segment_transcoded_video(
        #     video_file_extention=video_file_extention,
        #     video_filename_without_extention=video_filename_without_extention,
        #     local_video_path_with_extention=local_video_path_with_extention,
        #     local_video_path_without_extention=local_video_path_without_extention,
        # )

        # Segment the original video.
        self.segment_original_video(
            video_file_extention=video_file_extention,
            video_filename_without_extention=video_filename_without_extention,
            local_video_path_with_extention=local_video_path_with_extention,
            local_video_path_without_extention=local_video_path_without_extention,
        )

        # Task 02: Upload the video segments to S3.
        self.upload_segments_s3(
            video_file_extention=video_file_extention,
            video_filename_without_extention=video_filename_without_extention,
        )

        # Task 03: Clean up the local files.
        # cleanup_local_files_and_segments.delay(
        #     local_video_path_with_extention=local_video_path_with_extention,
        #     local_video_path_without_extention=local_video_path_without_extention,
        # )  # clearn up the local video

        # clean up the segments. 
        # mp4_segment_files_output_dir = f"{settings.DASH_LOCAL_VOD_SEGMENT_DIR_ROOT}/{video_filename_without_extention}/mp4"
        # cleanup_local_files_and_segments.delay(
        #     local_segments_path_dir=mp4_segment_files_output_dir
        # )

        try:

            # The local temporary manifest.mpd file path is: BASE_DIR/local-vod-segments-temp/UUID__rain-bg-video/mov/manifest.mpd
            # The S3 manifest.mpd file path is: vod-media/UUID__rain-calm-video/extention/manifest.mpd
            # EX: f"https://{s3_bucket_name}.s3.amazonaws.com/vod-media/{video_name}/extention/manifest.mpd"

            # Create mpd file paths.
            s3_mpd_path_mp4 = f"{settings.DASH_S3_FILE_ROOT}/{video_filename_without_extention}/mp4/manifest.mpd"
            s3_mpd_path_mov = f"{settings.DASH_S3_FILE_ROOT}/{video_filename_without_extention}/mov/manifest.mpd"

            db_data["mp4_s3_mpd_url"] = s3_mpd_path_mp4
            db_data["mov_s3_mpd_url"] = s3_mpd_path_mov
            print(db_data)

            serializer = VideoMetaDataSerializer(data=db_data)

            if serializer.is_valid(raise_exception=True):
                video_metadata = serializer.save()
                return JsonResponse(
                    {
                        "data": {
                            "status": "Upload Started",
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
