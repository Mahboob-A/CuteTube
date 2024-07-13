import os 

import logging 

from django.conf import settings

logger = logging.getLogger(__name__)


from celery import Celery, shared_task
from celery.signals import worker_process_init
import boto3
import os
from botocore.exceptions import ClientError


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
