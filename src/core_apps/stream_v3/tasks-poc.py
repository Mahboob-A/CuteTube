import os
import uuid
import subprocess
import logging


from django.conf import settings

from celery import shared_task
from celery.exceptions import Retry, RetryTaskError
from celery.signals import worker_process_init

import boto3
from botocore.exceptions import NoCredentialsError, ClientError, ConnectionError

from core_apps.stream_v3.signeltons import s3_client_vod_data_singleton


logger = logging.getLogger(__name__)



'''

A PoC code for Dash Processing Pipeline. The production code is in the tasks.py file.  

'''




# @shared_task
def process_and_save_video_local(request):
    """Takes 'request' as param from a POST API to process and save the video file in local storage."""

    raw_video_file = request.FILES["video"]
    title = request.data.get("title")
    description = request.data.get("description")
    duration = request.data.get("duration")

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
        settings.DASH_LOCAL_VOD_VIDEOS_DIR_ROOT, f"{video_filename_without_extention}"
    )

    # BASE_DIR/vod-media/local-vod-videos-temp/uuid__rain-bg-video.extention
    local_video_path_with_extention = os.path.join(
        settings.DASH_LOCAL_VOD_VIDEOS_DIR_ROOT,
        f"{video_filename_without_extention}{video_file_extention}",
    )

    with open(local_video_path_with_extention, "wb+") as video_file_destination:
        for chunk in raw_video_file.chunks():
            video_file_destination.write(chunk)
            print("writing")

    db_data = {
        "custom_video_title": video_filename_without_extention,  # without extention
        "title": title,
        "description": description,
        "duration": duration,
    }
    return (
        True,
        video_filename_without_extention,
        video_file_extention,
        local_video_path_with_extention,
        local_video_path_without_extention,
        db_data,
    )


@shared_task
def transcode_video_to_mov_or_mp4(
    local_video_path_with_extention, local_path_to_transcoded_video_with_extention
):
    "'Transcode the video into mov if original video is mp4 and vice versa."

    subprocess.run(
        [
            "ffmpeg",
            "-i",
            local_video_path_with_extention,
            "-map",
            "0",
            "-b:v",
            "4800k",
            "-s:v",
            "1920x1080",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            local_path_to_transcoded_video_with_extention,
        ]
    )


@shared_task
def dash_segment_video(local_video_path_with_extention, segment_files_output_dir):
    """Segment video file using ffmpeg.

    Local video (local_video_path_with_extention) is saved in: " src/vod-media/local-videos-temp/UUID__rain-bg-video.extention "  directory.

    Segments (output_dir) are saved in: " src/vod-media/segmented-videos-temp/ "


    """

    command = [
        "ffmpeg",
        "-i",
        local_video_path_with_extention,
        "-filter_complex",
        "[0:v]split=4[v1][v2][v3][v4]; [v1]scale=w=1980:h=1080[1080p]; [v2]scale=w=1280:h=720[720p]; [v3]scale=w=854:h=480[480p]; [v4]scale=w=640:h=360[360p]",
        "-map",
        "[1080p]",
        "-c:v:0",
        "libx264",
        "-b:v:0",
        "4800k",
        "-map",
        "[720p]",
        "-c:v:1",
        "libx264",
        "-b:v:1",
        "2400k",
        "-map",
        "[480p]",
        "-c:v:2",
        "libx264",
        "-b:v:2",
        "1200k",
        "-map",
        "[360p]",
        "-c:v:3",
        "libx264",
        "-b:v:3",
        "800k",
        "-map",
        "0:a?",
        "-init_seg_name",
        "init-stream$RepresentationID$.m4s",
        "-media_seg_name",
        "chunk-stream$RepresentationID$-$Number%05d$.m4s",
        "-use_template",
        "1",
        "-seg_duration",
        "4",
        "-adaptation_sets",
        "id=0,streams=v id=1,streams=a",
        "-f",
        "dash",
        os.path.join(segment_files_output_dir, "manifest.mpd"),
    ]

    try:
        subprocess.run(command, check=True)
        print("FFmpeg command executed successfully")

        # # Upload to S3
        # s3_bucket_name = "your-bucket-name"
        # # upload_dash_content(output_dir, s3_bucket_name, video_name)

        # # Cleanup local files
        # for root, dirs, files in os.walk(output_dir):
        #     for file in files:
        #         os.remove(os.path.join(root, file))
        # os.rmdir(output_dir)

        # return f"https://{s3_bucket_name}.s3.amazonaws.com/videos/{video_name}/manifest.mpd"
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg command failed: {e}")
        return None


# ############################### Upload Segments to S3 ###############################


# @worker_process_init.connect
# def init_worker_process(*args, **kwargs):
    """
    init_worker_process: Create single S3 Client object per Celery worker process.

    _extended_summary_
    To manage to overhead, and avoid race condition (if thread pool is used instead of prefork which is multiprocessing)
        creating single S3 client per celery worker process instead of:   (see S3Client_VoDData_Singleton implementation.)
            1. creating single S3 client for all celery worker process.
            2. creating individual S3 client for eash task.

    This will ensure each celery worker process has one S3 Client object as all the tasks under same worker process
    use same S3 Client object reducing race condition and reducing resource overhead.

    Returns:
        N/A.
    """
    # s3_client_vod_data_singleton.initialize()


@shared_task(bind=True, max_retries=5)
def upload_segment_batch_to_s3(self, s3_client, segment_batch: list):
    """Batch upload of segments in S3.

    A new task is created for a batch of segments, instead of new task for each individual segment,
    reducing the load of task creation.

    Ex: If a vidoe file has 80 segments, and batch size if 10, then total 8 task will be created,
    instead of 80 task as one task for each individual task.

    Args:
        segment_batch:
            A list of touples(local_single_segment_path, s3_file_path)

    """

    # One s3 client per celery worker process.
    # s3_client = s3_client_vod_data_singleton.get_client()
    # s3_client = s3_client_vod_data_singleton.initialize()
    failed_segment_uploads = {}

    if s3_client: 
        print("\nIn S3 upload handler: S3 client available")
    else: 
        print("\nIn S3 upload handler: S3 client is not available")
        
    for local_single_segment_path, s3_file_path in segment_batch:
        try:
            s3_client.upload_file(
                local_single_segment_path,
                settings.AWS_STORAGE_BUCKET_NAME,
                s3_file_path,
            )
            print("S3 file uploaded.")
        except FileNotFoundError as e:
            failed_segment_uploads[s3_file_path] = str(e)
            logger.exception(
                f"\n[XX Segment S3 Upload Error XX]: The Local Segment File: {local_single_segment_path} was not Found.\nException: {str(e)}"
            )
        except NoCredentialsError as e:
            failed_segment_uploads[s3_file_path] = str(e)
            logger.exception(
                f"\n[XX Segment S3 Upload Error XX]: S3 Credential Error.\nException: {str(e)}"
            )
        except ClientError as e:
            failed_segment_uploads[s3_file_path] = str(e)
            logger.warning(
                f"\n[XX Segment S3 Upload Error XX]: S3 Client Error.\nException: {str(e)}\nRetrying to upload: {local_single_segment_path}"
            )
            # Using Exponential Backoff to offload stress on the server.
            # Retrying the segment upload again, with maximum of 5 retries.
            if self.request.retries < self.max_retries:
                retry_in = 2**self.request.retries
                print("in retry: ", local_single_segment_path, " | retry in:  ", retry_in)
                raise self.retry(exc=e, countdown=retry_in)
        except Exception as e:
            failed_segment_uploads[s3_file_path] = str(e)
            logger.exception(
                f"\n[XX Segment S3 Upload Error XX]: Unexpected Error Occurred.\nException: {str(e)}"
            )
        print("Failed segmets: ", failed_segment_uploads)


@shared_task
def upload_dash_segments_to_s3(
    video_file_extention: str,
    local_video_main_segments_dir_path: str,
    video_filename_without_extention: str,
):
    """
    upload_dash_segments_to_s3: Main Entrypoint function to upload local single segment file by batch processing in S3 Bucket.

    Arguments:
        local_video_main_segments_dir_path {str} -- Main directory where all the segments are stored.
        video_filename_without_extention {str} -- video filename without extention. Ex: UUID__rain-calm-video

    Return:
        True:
            If upload successful.
        False:
            If upload unsuccessful.
    """

    s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
    try:

        # S3 File Structure: vod-media/UUID__rain-calm-video/extention/all-segment-files and mpd file
        s3_main_file_path = f"{settings.DASH_S3_FILE_ROOT}/{video_filename_without_extention}/{video_file_extention}"

        segment_batch = []
        segment_batch_size = 10
        # all_tasks = []

        for root, dirs, files in os.walk(local_video_main_segments_dir_path):
            for file in files:
                print("\nIn Main S3 Upload: File: ", file)
                local_single_segment_path = os.path.join(root, file)
                print("Local segment file path: ", local_single_segment_path)
                s3_file_path = os.path.join(s3_main_file_path, file)
                # relative_path = os.path.relpath(
                #     local_single_segment_path, local_video_main_segments_dir_path
                # )

                # Tuple[0]: local single segment file path.
                # Tuple[1]: s3 file path for s3 bucket
                segment_batch.append((local_single_segment_path, s3_file_path))

                if len(segment_batch) >= segment_batch_size:
                    upload_segment_batch_to_s3.delay(s3_client, segment_batch)
                    # all_tasks.append(task)
                    segment_batch = []

        # If the segment_batch size is < 10
        if segment_batch:
            upload_segment_batch_to_s3.delay(s3_client, segment_batch)
            # all_tasks.append(task)
        # return all_tasks
        return True
    except Exception as e:
        logger.exception(
            f"\n[XX Segment S3 Upload Error XX]: Unexpected Error Occurred.\nException: {str(e)}"
        )
        return None


# ##################### Cleanup Local Segment Files After S3 Upload Completed. ######################


@shared_task
def cleanup_local_files_and_segments(
    local_video_path_with_extention: str = None,
    local_video_path_without_extention: str = None,
    local_segments_path_dir: str = None,
):
    """Task to delete local video file and its directory or the segments and their directory"""

    if local_video_path_with_extention and os.path.isfile(
        local_video_path_with_extention
    ):
        os.remove(local_video_path_with_extention)  # remove the file
        os.rmdir(local_video_path_without_extention) # remove the dir 
    else:

        for root, dirs, files in os.walk(local_segments_path_dir):
            for file in files:
                os.remove(os.path.join(root, file))

        os.rmdir(local_segments_path_dir)


#  ## For local testing.


# local_video_segment_path = "/home/mehboob/poridhi-codes/cls-02-node-js-project/cutetube/src/vod-media/anime-village-lifestyle-segs"
# local_video_main_segments_dir_path = (
#     "/home/mehboob/poridhi-codes/cls-02-node-js-project/cutetube/src/vod-media/"
# )

# original_video_filename_without_extention = "ok"

# upload_dash_segments_to_s3(
#     local_video_main_segments_dir_path=local_video_main_segments_dir_path,
#     original_video_filename_without_extention=original_video_filename_without_extention
# )
