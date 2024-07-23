import os
import uuid
import logging


from django.conf import settings


logger = logging.getLogger(__name__)


def process_and_save_video_local_drm_v4(request):
    """A util function to save the vidoe in local storage
    and create required directories and files for Dash Processing Pipeline.

    Input:
        request: A Django http.request object.

    Return:
        A dict of processed data.
    """

    try:

        raw_video_file = request.FILES["video"]
        title = request.data.get("title")
        description = request.data.get("description")
        duration = request.data.get("duration")

        # The video file name is made with the original file embaded file name, not with the reqeuest body video content title.
        video_file_basename = os.path.splitext(raw_video_file.name)[
            0
        ]  # original video name without extention (ex: calm-rain-video)
        video_file_extention = os.path.splitext(raw_video_file.name)[
            1
        ]  # video extention (ex: .mp4)

        video_filename_without_extention = f"{uuid.uuid4()}__{video_file_basename}"  # uuid__video_name_without_extention (Ex: uuid__calm_rain_video)

        # BASE_DIR/vod-media/local-vod-videos-temp/
        if not os.path.exists(settings.DASH_LOCAL_VOD_VIDEOS_DIR_ROOT):
            os.mkdir(settings.DASH_LOCAL_VOD_VIDEOS_DIR_ROOT)

        # BASE_DIR/vod-media/local-vod-videos-temp/uuid__rain-bg-video and without extention like:  .mp4 or .mov
        local_video_path_without_extention = os.path.join(
            settings.DASH_LOCAL_VOD_VIDEOS_DIR_ROOT,
            f"{video_filename_without_extention}",
        )

        # BASE_DIR/vod-media/local-vod-videos-temp/uuid__rain-bg-video.extention
        local_video_path_with_extention = os.path.join(
            settings.DASH_LOCAL_VOD_VIDEOS_DIR_ROOT,
            f"{video_filename_without_extention}{video_file_extention}",
        )

        with open(local_video_path_with_extention, "wb+") as video_file_destination:
            for chunk in raw_video_file.chunks():
                video_file_destination.write(chunk)

        db_data = {
            "custom_video_title": video_filename_without_extention,  # without extention
            "title": title,
            "description": description,
            "duration": duration,
        }

        # Dir creation to store mp4 and mov segment files. #

        # BASE_DIR/local-vod-segments-temp/UUID__rain-bg-video/mp4
        mp4_segment_files_output_dir = f"{settings.DASH_LOCAL_VOD_SEGMENT_DIR_ROOT}/{video_filename_without_extention}/mp4"

        os.makedirs(mp4_segment_files_output_dir, exist_ok=True)

        # BASE_DIR/local-vod-segments-temp/UUID__rain-bg-video/mov
        mov_segment_files_output_dir = f"{settings.DASH_LOCAL_VOD_SEGMENT_DIR_ROOT}/{video_filename_without_extention}/mov"

        os.makedirs(mov_segment_files_output_dir, exist_ok=True)

        logger.info(
            f"\n[=> Process and Save Video Local SUCCESS]: Video save to local and segment dirs for mp4 and mov Creation is Successful."
        )

        return {
            "status": True,
            "video_file_extention": video_file_extention,
            "video_filename_without_extention": video_filename_without_extention,
            "local_video_path_with_extention": local_video_path_with_extention,
            "local_video_path_without_extention": local_video_path_without_extention,
            "mp4_segment_files_output_dir": mp4_segment_files_output_dir,
            "mov_segment_files_output_dir": mov_segment_files_output_dir,
            "db_data": db_data,
        }
    except Exception as e:
        logger.error(
            f"\n[XX Process and Save Video Local XX]: Video save to local and segment dirs for mp4 and mov Creation Failed.\nEXCEPTION: {str(e)}"
        )
        return {"status": False, "error": str(e)}
