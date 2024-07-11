import os
import uuid
import subprocess
import logging


from django.conf import settings

from celery import shared_task
from celery.exceptions import Retry, RetryTaskError

import boto3
from botocore.exceptions import NoCredentialsError


logger = logging.getLogger(__name__)


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

    video_filename_without_extention = (
        f"{uuid.uuid4()}__{video_file_basename}"  # uuid__video_name_without_extention (Ex: uuid__calm_rain_video)
    )

    # save in local dir.
    local_video_dir = os.path.join(settings.DASH_FILE_ROOT, "local-videos-temp")

    if not os.path.exists(local_video_dir):
        os.mkdir(local_video_dir)

    local_video_path_without_extention = os.path.join(
        local_video_dir, f"{video_filename_without_extention}"
    ) # without .mp4 or .mov 

    local_video_path_with_extention = os.path.join(
        local_video_dir, f"{video_filename_without_extention}{video_file_extention}"
    )

    with open(local_video_path_with_extention, "wb+") as video_file_destination:
        for chunk in raw_video_file.chunks():
            video_file_destination.write(chunk)

    db_data = {
        "original_video_title": video_filename_without_extention,  # without extention
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
    local_video_path_without_extention, video_file_extention
):
    "'Transcode the video into mov if original video is mp4 and vice versa."

    if video_file_extention == ".mp4":
        mov_video_file_path = os.path.join(local_video_path_without_extention, ".mov")

        local_video_path_with_extention = f"{local_video_path_without_extention}{video_file_extention}"

        subprocess.run([
            'ffmpeg', '-i', local_video_path_with_extention, '-map', '0', '-b:v', '2400k',
            '-s:v', '1920x1080', '-c:v', 'libx264', '-c:a', 'aac', mov_video_file_path
        ])
        return mov_video_file_path, video_file_extention

    elif video_file_extention == ".mov":
        mp4_video_file_path = os.path.join(local_video_path_without_extention, ".mp4")

        local_video_path_with_extention = f"{local_video_path_without_extention}{video_file_extention}"

        subprocess.run([
            'ffmpeg', '-i', local_video_path_with_extention, '-map', '0', '-b:v', '2400k',
            '-s:v', '1920x1080', '-c:v', 'libx264', '-c:a', 'aac', mp4_video_file_path
        ])
        return mp4_video_file_path, video_file_extention


@shared_task
def segment_video(local_video_file_with_extention, video_name, output_dir):
    """Segment video file using ffmpeg.

    Local video (local_video_file_with_extention) is saved in: " src/vod-media/local-videos-temp/ "  directory.

    Segments (output_dir) are saved in: " src/vod-media/segmented-videos-temp/ "
    
    
    """

    command = [
        'ffmpeg', '-i', local_video_file_with_extention,
        '-filter_complex',
        "[0:v]split=4[v1][v2][v3][v4]; [v1]scale=w=1980:h=1080[1080p]; [v2]scale=w=1280:h=720[720p]; [v3]scale=w=854:h=480[480p]; [v4]scale=w=640:h=360[360p]",
        '-map', '[1080p]', '-c:v:0', 'libx264', '-b:v:0', '5000k',
        '-map', '[720p]', '-c:v:1', 'libx264', '-b:v:1', '3000k',
        '-map', '[480p]', '-c:v:2', 'libx264', '-b:v:2', '1500k',
        '-map', '[360p]', '-c:v:3', 'libx264', '-b:v:3', '800k',
        '-map', '0:a',
        '-init_seg_name', 'init-stream$RepresentationID$.m4s',
        '-media_seg_name', 'chunk-stream$RepresentationID$-$Number%05d$.m4s',
        '-use_template', '1',
        '-seg_duration', '4',
        '-adaptation_sets', 'id=0,streams=v id=1,streams=a',
        '-f', 'dash',
        os.path.join(output_dir, 'manifest.mpd')
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



def _upload_to_s3(s3_obj, local_file_path: str, s3_file_path: str):
    '''Local_File_Path is the local storage single segment file path.'''
    try:
        s3_obj.upload_file(
            local_file_path, settings.AWS_STORAGE_BUCKET_NAME, s3_file_path
        )
        return True 
    except FileNotFoundError as e: 
        logger.exception(f"\n[XX Segment S3 Upload Error XX]: The Local Segment File: {local_file_path} was not Found.\nException: {str(e)}")      
        return None 
    except Exception as e: 
        logger.exception(f"\n[XX Segment S3 Upload Error XX]: Unexpected Error Occurred.\nException: {str(e)}")
        return None 


@shared_task
def upload_dash_segments_to_s3(local_video_main_segments_dir_path, video_filename_without_extention):
    """
    upload_dash_segments_to_s3: Upload local single segment file in S3 Bucket. 

    Arguments:
        local_video_main_segments_dir_path {str} -- Main directory where all the segments are stored. 
        original_video_filename_without_extention {str} -- original video filename without extention. Ex: UUID__rain-calm-video
    
    Return: 
        True: 
            If upload successful. 
        False: 
            If upload unsuccessful. 
    """
    try:
        max_s3_upload_retry = 5 
        
        s3_obj = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        s3_main_file_path = f"vod-media/{video_filename_without_extention}/" 
        
        failed_upload_segments = {}

        for root, dirs, files in os.walk(local_video_main_segments_dir_path):
            for file in files:
                local_single_segment_path = os.path.join(root, file)
                relative_path = os.path.relpath(
                    local_single_segment_path, local_video_main_segments_dir_path
                )
                s3_file_path = os.path.join(s3_main_file_path, file)
                
                # Uploading to S3.
                is_success = _upload_to_s3(s3_obj=s3_obj, local_file_path=local_single_segment_path, s3_file_path=s3_file_path)
                
                # If a segment is failed to be uploaded, trying 5 times to upload it. 
                if is_success is None: 
                    for retry in range(max_s3_upload_retry):
                        is_success = _upload_to_s3(s3_obj=s3_obj, local_file_path=local_single_segment_path, s3_file_path=s3_file_path)
                        # time.sleep(5) # should I use time to give some time for the network call?
                        if is_success:
                            break 
                    max_s3_upload_retry = 5 
                    if not is_success:
                        failed_upload_segments[file] = local_single_segment_path
                    
                    
        return True, failed_upload_segments
            
    except NoCredentialsError as e:
        logger.exception(
            f"\n[XX Segment S3 Upload Error XX]: S3 Credential Error.\nException: {str(e)}"
        )
        return None, None
    except Exception as e: 
        logger.exception(f"\n[XX Segment S3 Upload Error XX]: Unexpected Error Occurred.\nException: {str(e)}")
        return None, None 

# local_video_segment_path = "/home/mehboob/poridhi-codes/cls-02-node-js-project/cutetube/src/vod-media/anime-village-lifestyle-segs"
# local_video_main_segments_dir_path = (
#     "/home/mehboob/poridhi-codes/cls-02-node-js-project/cutetube/src/vod-media/"
# )

# original_video_filename_without_extention = "ok"

# upload_dash_segments_to_s3(
#     local_video_main_segments_dir_path=local_video_main_segments_dir_path,
#     original_video_filename_without_extention=original_video_filename_without_extention
# )
