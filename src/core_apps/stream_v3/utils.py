import os
import uuid
import logging


from django.conf import settings


logger = logging.getLogger(__name__)


def process_and_save_video_local(request):
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


# Testing Other Concepts.

"""

cwd = "/home/mehboob/poridhi-codes/cls-02-node-js-project/cutetube/src/raw-vides/anime-village-lifestyle.mp4"


file_name = os.path.basename(cwd)

print(file_name)

# Global variable to hold the S3 client
s3_client = None


@worker_process_init.connect
def init_worker_process(*args, **kwargs):
    global s3_client
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )


@shared_task(bind=True, max_retries=5)
def upload_segment_batch(self, segment_batch):
    global s3_client
    failed_uploads = {}

    for local_path, s3_path in segment_batch:
        try:
            s3_client.upload_file(local_path, settings.AWS_STORAGE_BUCKET_NAME, s3_path)
        except FileNotFoundError as e:
            logger.exception(f"File not found: {local_path}. Error: {str(e)}")
            failed_uploads[s3_path] = str(e)
        except ClientError as e:
            logger.warning(f"S3 upload failed for {s3_path}. Error: {str(e)}")
            if self.request.retries < self.max_retries:
                retry_in = 2**self.request.retries
                raise self.retry(countdown=retry_in)
            failed_uploads[s3_path] = str(e)
        except Exception as e:
            logger.exception(f"Unexpected error uploading {s3_path}. Error: {str(e)}")
            failed_uploads[s3_path] = str(e)

    return failed_uploads


@shared_task
def upload_dash_segments_to_s3(
    local_video_main_segments_dir_path, video_filename_without_extention
):
    s3_main_file_path = f"vod-media/{video_filename_without_extention}/"

    segment_batch = []
    batch_size = 10  # Adjust based on your needs
    tasks = []

    for root, dirs, files in os.walk(local_video_main_segments_dir_path):
        for file in files:
            local_single_segment_path = os.path.join(root, file)
            s3_file_path = os.path.join(s3_main_file_path, file)

            segment_batch.append((local_single_segment_path, s3_file_path))

            if len(segment_batch) >= batch_size:
                task = upload_segment_batch.delay(segment_batch)
                tasks.append(task)
                segment_batch = []

    # Don't forget the last batch if it's not empty
    if segment_batch:
        task = upload_segment_batch.delay(segment_batch)
        tasks.append(task)

    return tasks

"""
