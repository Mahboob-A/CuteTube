import logging

from django.http import JsonResponse
from django.conf import settings


from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, MultiPartParserError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError


from celery import chain, group

# Local Imports
from core_apps.stream_v3.models import VideoMetaData
from core_apps.stream_v3.serializers import VideoMetaDataSerializer
from core_apps.stream_v3.utils import process_and_save_video_local

# Celery Tasks
from core_apps.stream_v3.tasks import (
    transcode_video_to_mov_or_mp4,
    dash_processing_entrypoint,
    dash_segment_video,
    upload_dash_segments_to_s3,
)


logger = logging.getLogger(__name__)


class UploadVideoVoDAPI(APIView):
    """API to upload video in CuteTube platform by users."""

    parser_classes = [MultiPartParser]
    permission_classes = [AllowAny]  # TODO: change to is authenticated in production.

    def start_dash_processing_pipeline(
    self, 
    video_file_extention: str,
    video_filename_without_extention: str,
    local_video_path_with_extention: str,
    local_video_path_without_extention: str,
    mp4_segment_files_output_dir: str,
    mov_segment_files_output_dir: str,
):

        '''
        Dash Processing Pipeline Generate Entrypoint. 
        A util method to begin the dash processing pipeline. 
        
        The Pipeline is structured as per following tasks: 
        
            - A single group of tasks as entrypoint (The group contains the below two tasks - an individual task and a innner group of tasks) 
            
                - transcode original video to other format - an individual task (MP4 and MOV vice-versa)
                
                - Create chain of tasks for each video file: (The below process is followed for both of the video file)
                
                    - The each chain has the following tasks: 
                        - an entrypoint task to begin the video processing 
                        - segment the video into 4 formats (360, 480, 720 and 1080 with appropriate format)
                        - upload to S3 task: 
                            - this task uploads the segments as a batch creating subtasks and another inner chain and a chord
                            - a cleanup task as a callback to the chord to cleanup all local files after the upload to S3 batch processing is completed. 
                
                    - Start the pipeline 
        
        '''

        to_be_transcode_file_extention = (
            ".mov" if video_file_extention == ".mp4" else ".mp4"
        )

        # Original and to be transcoded video file are stored in same directory, but their extention is different.
        to_be_transcode_file_path_with_extention = (
            f"{local_video_path_without_extention}{to_be_transcode_file_extention}"
        )

        to_be_transcode_file_task = transcode_video_to_mov_or_mp4.s(
            local_video_path_with_extention,
            to_be_transcode_file_path_with_extention,
        )

        # # Chain for original file format
        original_dash_processing_chain = chain(
            dash_processing_entrypoint.s(
                video_file_extention,
                video_filename_without_extention,
                local_video_path_with_extention,
                local_video_path_without_extention,
                mp4_segment_files_output_dir,
                mov_segment_files_output_dir,
            ),
            dash_segment_video.s(),
            upload_dash_segments_to_s3.s(),
        )

        # Chain for other file format
        transcoded_dash_processing_chain = chain(
            dash_processing_entrypoint.s(
                to_be_transcode_file_extention,
                video_filename_without_extention,
                to_be_transcode_file_path_with_extention,
                local_video_path_without_extention,
                mp4_segment_files_output_dir,
                mov_segment_files_output_dir,
            ),
            dash_segment_video.s(),
            upload_dash_segments_to_s3.s(),
        )

        """Final Chain: 
            A. 1st Task: Transcode the original video to other format i.e. (MP4 and MOV vice-versa)
            B. 2nd Task: A Group for multiprocessing of other Two Chain - This Chain is under a Chord - The Callback of the Chord is Cleanup Local Files Task
                a. original_dash_processing_chain - tasks: ()
                    - Begin the processing
                    - Segment the video in 4 formats (360, 480, 720, 1080 with appropriate bitrate)
                    - Upload to S3 Task 
                        - The cleanup callback cleansup the local files 
        """
        full_dash_pipeline = chain(
            to_be_transcode_file_task,
            group(original_dash_processing_chain, transcoded_dash_processing_chain),
        )

        full_dash_pipeline.apply_async(countdown=5)

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
                {"data": {"status": "error", "detail": "No video file provided. Supported video type is .MP4 and .MOV"}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        result = process_and_save_video_local(request=request)
        if result["status"] is True:
            video_file_extention = result["video_file_extention"]
            video_filename_without_extention = result[
                "video_filename_without_extention"
            ]
            local_video_path_with_extention = result[
                "local_video_path_with_extention"
            ]
            local_video_path_without_extention = result[
                "local_video_path_without_extention"
            ]
            mp4_segment_files_output_dir = result["mp4_segment_files_output_dir"]
            mov_segment_files_output_dir = result["mov_segment_files_output_dir"]
            db_data = result["db_data"]

        elif result["status"] is False:
            logger.error(
                f"\n[XX UploadVideoVoDAPI ERROR XX]: Request was not satisfied. Unexpected error occurred.\nError: {result.get('error')}"
            )
            return Response(
                {
                    "data": {
                        "status": "error",
                        "detail": "It's not you, It's Us. Unexpected error occurred.",
                    }
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if video_file_extention not in [".mov", ".mp4"]:
            return Response(
                {"error": "Unsuppored video format. Only .mp4 and .mov supported"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # The Dash Processing Pipeline
        # self.start_dash_processing_pipeline(
        #     video_file_extention=video_file_extention,
        #     video_filename_without_extention=video_filename_without_extention,
        #     local_video_path_with_extention=local_video_path_with_extention,
        #     local_video_path_without_extention=local_video_path_without_extention,
        #     mp4_segment_files_output_dir=mp4_segment_files_output_dir,
        #     mov_segment_files_output_dir=mov_segment_files_output_dir
        # )

        try:

            # The local temporary manifest.mpd file path is: BASE_DIR/local-vod-segments-temp/UUID__rain-bg-video/mov/manifest.mpd
            # The S3 manifest.mpd file path is: vod-media/UUID__rain-calm-video/extention/manifest.mpd
            # EX: f"https://{s3_bucket_name}.s3.amazonaws.com/vod-media/{video_name}/extention/manifest.mpd"

            # NOTE: In future release, create links based on the Dash Pipeline Event.
            mp4_s3_mpd_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{settings.DASH_S3_FILE_ROOT}/{video_filename_without_extention}/mp4/manifest.mpd"
            mov_s3_mpd_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{settings.DASH_S3_FILE_ROOT}/{video_filename_without_extention}/mov/manifest.mpd"

            db_data["mp4_s3_mpd_url"] = mp4_s3_mpd_url
            db_data["mov_s3_mpd_url"] = mov_s3_mpd_url
            print(db_data)

            serializer = VideoMetaDataSerializer(data=db_data)

            if serializer.is_valid(raise_exception=True):
                video_metadata = serializer.save()
                print("\nserializer data: ", serializer.data)
                print("video file name: ", video_filename_without_extention)
                print("video extention: ", video_file_extention)
                return JsonResponse(
                    {
                        "data": {
                            "status": "Upload Started",
                            "video_id": video_metadata.id,
                            "video_name_without_extention": video_filename_without_extention,
                            "video_extention": video_file_extention,
                        }
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
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
            return Response(
                {
                    "data": {
                        "status": "error",
                        "detail": "It's not you, It's Us. Unexpected error occurred.",
                    }
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class StreamVideoVoDAPI(APIView):
    '''Stream API for CuteTube. 
    
    The API provides the S3 MPD file URL to the client provided a video ID.
    '''

    def get(self, request, video_id): 
        '''Return S3 MPD file URL of the video_ID '''

        try: 
            video_metadata = VideoMetaData.objects.get(id=video_id)
            serializer = VideoMetaDataSerializer(video_metadata)
            return Response({"data": {"status": "success", "data": serializer.data}}, status=status.HTTP_200_OK)
        except VideoMetaData.DoesNotExist as err: 
            return Response({"data": {"status": "error", "detail": f"Video ID: {video_id} is invalid."}}, status=status.HTTP_404_NOT_FOUND)
