import os
import uuid
import subprocess
import logging


from django.conf import settings

from celery import shared_task, group, chord
from celery.exceptions import Retry, RetryTaskError
from celery.signals import worker_process_init

import boto3
from botocore.exceptions import NoCredentialsError, ClientError, ConnectionError

from core_apps.stream_v3.signeltons import s3_client_vod_data_singleton


logger = logging.getLogger(__name__)

# ############################# Tasks Sections # ##################################


# Entrypoint for Dash Processing Pipeline
@shared_task(bind=True, max_retries=3)
def transcode_video_to_mov_or_mp4(
    self,
    original_video_path_with_extention,
    local_path_to_transcod_video_with_extention,
):
    """Transcode the video into mov if original video is mp4 and vice versa.

    Note: If and Only If Transcode Task is successfull, then only the Segmentation and Upload to S3 Process will begin.
    """

    logger.info(
        f'''
        \n[=> TRANSCODE VIDEO - DASH PIPELINE ENTRYPOINT]: Transcode Details -
        Original Video: {original_video_path_with_extention}
        To Be Transcoded To: {local_path_to_transcod_video_with_extention}
        
        Segmentation, S3 Upload and Cleanup are Awaiting ... 
        '''
    )

    command = [
        "ffmpeg",
        "-i",
        original_video_path_with_extention,
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
        local_path_to_transcod_video_with_extention,
    ]

    try:
        subprocess.run(command, check=True)
        logger.info(
            f"\n[=> DASH TRANSCODE VIDEO SUCCESS]: Task {transcode_video_to_mov_or_mp4.name}: FFmpeg command to transcode file - {original_video_path_with_extention} executed successfully"
        )
        return {
            "status": "success",
            "transcode_video_to_mov_or_mp4_status": "video transcoded successfully",
        }
    except subprocess.CalledProcessError as e:
        logger.error(
            f"\n[XX DASH TRANSCODE VIDEO ERROR XX]: Task {transcode_video_to_mov_or_mp4.name}: FFmpeg command to transcode file - {original_video_path_with_extention}  failed\n[Exception]: {str(e)}"
        )
        if self.request.retries < self.max_retries:
            retry_in = 2**self.request.retries
            logger.warning(
                f"\n[## TRANSCODE VIDEO WARNING]: Ffmpeg Command to Transcode Video Rerying in: {retry_in}.\nError: {str(e)}"
            )
            self.retry(exc=e, countdown=retry_in)
        return {
            "status": "failure",
            "transcode_video_to_mov_or_mp4_status": "video transcode failed",
        }
    except Exception as e:
        logger.warning(
            f"\n[## TRANSCODE VIDEO ERROR]: Ffmpeg Command to Transcode Video Failed\nError: {str(e)}"
        )
        return {
            "status": "failure",
            "transcode_video_to_mov_or_mp4_status": "video transcod failed",
        }


# Entrypoing for Dash Segment and S3 upload pipeline
@shared_task
def dash_processing_entrypoint(
    preprocessing_result,
    video_file_extention: str,
    video_filename_without_extention: str,
    local_video_path_with_extention: str,
    local_video_path_without_extention: str,
    mp4_segment_files_output_dir: str,
    mov_segment_files_output_dir: str,
):
    """Main Entrypoint of Chain of Tasks.

    Task to pre-process the transcode and segments directories.

    Return:
            All the necesary directory paths to store transcode and segment files by ffmpeg.
    """

    try:

        logger.info(
            f"\n\n[=> DASH PROCESSING ENTRYPOINT]: Segmentation, S3 Upload and Cleanup is about to Start for Video FIle: {local_video_path_with_extention}."
        )

        # This preprocessing is returned from the Transcodin Video task - which is inside a chain as individual task in the pipeline. See the view for more details.
        if preprocessing_result["status"] == "failure":
            error = preprocessing_result["error"]
            logger.error(
                f"\n[XX DASH TRANSCODE VIDEO ERROR XX]: Previous Task ('transcode_video_to_mov_or_mp4') Failed.\nFail Reason: {error}\nSkipping the {dash_processing_entrypoint.name} Task."
            )
            return preprocessing_result

        return {
            "status": "success",
            "dash_processing_entrypoint_status": "dash_processing_started",
            "video_file_extention": video_file_extention,
            "video_filename_without_extention": video_filename_without_extention,
            "local_video_path_with_extention": local_video_path_with_extention,
            "local_video_path_without_extention": local_video_path_without_extention,
            "mp4_segment_files_output_dir": mp4_segment_files_output_dir,
            "mov_segment_files_output_dir": mov_segment_files_output_dir,
        }
    except Exception as e:
        logger.error(
            f"\n[XX DASH PROCESSING ENTRYPOINT ERROR XX]: Task {dash_processing_entrypoint.name} Failed.\nEXCEPTION: {str(e)}"
        )
        return {"status": "failure", "error": str(e)}


@shared_task
def dash_segment_video(preprocessing_result: dict):
    """Segment video file using ffmpeg.

    1. Each task other than " process_dirs_for_transcode_and_segments " takes a dictionary of paths: preprocessing_result

    2. dash_segment_video - Working parameters.

        - video_file_extention
        - local_video_path_with_extention
        - mp4_segment_files_output_dir or mov_segment_files_output_dir

    3. Explanation:

                I. video_file_extention
                        - The extention of the video file

                II. local_video_path_with_extention:
                        - The video file that needs to be segmented.
                        - currently the file is saved in this directory  strucutre:  src/vod-media/local-videos-temp/UUID__rain-bg-video.extention (mov/mp4)

                III. mp4_segment_files_output_dir or mov_segment_files_output_dir:
                        - The directory where the output file for the segmentation will be saved depending upon the video extention file
                        - Currently the segmented files are stored in this directory structure: src/vod-media/segmented-videos-temp/UUID__rain-bg-video/extention(mov/mp4)/chunks and manifest.mpd
    """

    if preprocessing_result["status"] == "failure":
        error = preprocessing_result["error"]
        logger.error(
            f"\n[XX DASH SEGMENT VIDEO ERROR XX]: Previous Task ('dash_processing_entrypoint or transcode_video_to_mov_or_mp4') Failed.\nFail Reason: {error}\nSkipping the {dash_segment_video.name} Task."
        )
        return preprocessing_result

    video_file_extention = preprocessing_result["video_file_extention"]
    local_video_path_with_extention = preprocessing_result[
        "local_video_path_with_extention"
    ]

    logger.info(
        f"\n\n[=> DASH SEGMENT VIDEO STARTED]: DASH Segmentation Started for Video File: {local_video_path_with_extention}"
    )
    
    if video_file_extention == ".mp4":
        mp4_segment_files_output_dir = preprocessing_result[
            "mp4_segment_files_output_dir"
        ]
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
            os.path.join(mp4_segment_files_output_dir, "manifest.mpd"),
        ]

    elif video_file_extention == ".mov":
        mov_segment_files_output_dir = preprocessing_result[
            "mov_segment_files_output_dir"
        ]
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
            os.path.join(mov_segment_files_output_dir, "manifest.mpd"),
        ]

    try:
        subprocess.run(command, check=True)
        logger.info(
            f"\n[=> DASH SEGMENT VIDEO SUCCESS]: Task {dash_segment_video.name}: FFmpeg command executed successfully"
        )
        preprocessing_result["status"] = "success"
        preprocessing_result["dash_segment_video_status"] = (
            "segmentation is successfull"
        )
        return preprocessing_result

    except subprocess.CalledProcessError as e:
        logger.error(
            f"\n[XX DASH SEGMENT VIDEO SUCCESS ERROR XX]: Task {dash_segment_video.name}: FFmpeg command failed\n[Exception]: {e}"
        )
        preprocessing_result["status"] = "failure"
        preprocessing_result["dash_segment_video_status"] = (
            "segmentation is un-successfull"
        )
        preprocessing_result["error"] = "segmentation failed"
        preprocessing_result["dash_segment_video_error"] = str(e)
        return preprocessing_result

    except Exception as e:
        logger.error(
            f"\n[XX DASH SEGMENT VIDEO SUCCESS ERROR XX]: Task {dash_segment_video.name}: FFmpeg command failed\n[Exception]: {e}"
        )
        preprocessing_result["status"] = "failure"
        preprocessing_result["error"] = str(e)
        return preprocessing_result

    # ############################### Upload Segments to S3 ###############################


@worker_process_init.connect
def init_worker_process(*args, **kwargs):
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
    s3_client_vod_data_singleton.initialize()


# Sub Task to upload segments as batch upload to S3 (created by: upload_dash_segments_to_s3 task)
@shared_task(bind=True, max_retries=5)
def upload_segment_batch_to_s3_sub_task(self, segment_batch: list):
    """Batch upload of segments in S3.

    A new task is created for a batch of segments, instead of new task for each individual segment,
    reducing the load of task creation.

    Ex: If a vidoe file has 80 segments, and batch size if 10, then total 8 task will be created,
    instead of 80 task as one task for each individual task.

    Args:
        segment_batch:
            A list of touples(local_single_segment_path, s3_file_path)

    """

    # One s3 client per celery worker process. created using celery singal. The S3 client class is Singleton.
    s3_client = s3_client_vod_data_singleton.get_client()

    failed_segment_uploads = {}
    
    # NOTE: for future updates, implement Sentry or other logging mechanism to get the failed uploads.

    total_segments = len(segment_batch)
    uploaded_segments = 0

    for local_single_segment_path, s3_file_path in segment_batch:
        try:
            s3_client.upload_file(
                local_single_segment_path,
                settings.AWS_STORAGE_BUCKET_NAME,
                s3_file_path,
            )
            uploaded_segments += 1
            upload_progress = (uploaded_segments / total_segments) * 100

            logger.info(
                f"[=> SEGMENT S3 UPLOAD PROGRESS]: {upload_progress:.2f}% ({uploaded_segments}/{total_segments}).\nUploaded Chunk: {os.path.basename(s3_file_path)}"
            )

        except FileNotFoundError as e:
            failed_segment_uploads[s3_file_path] = str(e)
            logger.exception(
                f"\n[XX SEGMENT S3 UPLOAD ERROR XX]: The Local Segment File: {local_single_segment_path} was not Found.\nException: {str(e)}"
            )

        except NoCredentialsError as e:
            failed_segment_uploads[s3_file_path] = str(e)
            logger.exception(
                f"\n[XX Segment S3 Upload Error XX]: S3 Credential Error.\nException: {str(e)}"
            )

        except ClientError as e:
            logger.warning(
                f"\n[XX SEGMENT S3 UPLOAD ERROR XX]: S3 Client Error.\nException: {str(e)}\nRetrying to upload: {local_single_segment_path}"
            )
            # Using Exponential Backoff to offload stress on the server.
            # Retrying the segment upload again, with maximum of 5 retries.
            if self.request.retries < self.max_retries:
                retry_in = 2**self.request.retries
                logger.warning(
                    f"\n[## SEGMENT S3 UPLOAD WARNING ]: Chunk {os.path.basename(s3_file_path)} Couldn't be Uploaded.\nRetrying in: {retry_in}."
                )
                raise self.retry(exc=e, countdown=retry_in)

            # only count as failed segment when the max retries is exceeded.
            failed_segment_uploads[s3_file_path] = str(e)
            # NOTE: For future update, implement logging mechanism to trace the failed uploads here.

        except Exception as e:
            failed_segment_uploads[s3_file_path] = str(e)
            logger.exception(
                f"\n[XX SEGMENT S3 UPLOAD ERROR XX]: Unexpected Error Occurred. Segments couldn't be uploaded to S3.\nException: {str(e)}"
            )

    # Result of batch upload.
    if failed_segment_uploads:
        logger.exception(
            f"\n[XX SEGMENT S3 UPLOAD ERROR XX]: Some Segments Couldn't be Uploaded.\nNOTE TO ME: Integrate Sentry or other Retry Mechanism to Upload the Failed Segments.\nFailed Segments: {failed_segment_uploads}"
        )
        return "failure"
    else:
        logger.info(f"\n[=> SEGMENT S3 UPLOAD SUCCESS]: Segment Batch UPLOAD SUCCESS.")
        return "success"


# Main Entrypoint task to upload segment to S3
@shared_task
def upload_dash_segments_to_s3(preprocessing_result: dict):
    """
    upload_dash_segments_to_s3: Main Entrypoint function to upload local single segment file by batch processing in S3 Bucket.

    Main Parameter: preprocessing_result - A dictionary of dirctories and status of completion of previous task.

    Working Parameters:

        - video_file_extention:
                - Video file extention.

        - video_filename_without_extention:
                - Video filename without extention. Ex: UUID__rain-calm-video

        - mp4_segment_files_output_dir or mov_segment_files_output_dir:
                - The directory where the output file for the segmentation will be saved depending upon the video extention file
                - Currently the segmented files are stored in this directory structure: src/vod-media/segmented-videos-temp/UUID__rain-bg-video/extention(mov/mp4)/chunks and manifest.mpd

    Return:
        - preprocessing_result dict with status of the task.

    """

    if preprocessing_result["status"] == "failure":
        error = preprocessing_result["error"]
        logger.error(
            f"[XX MAIN DASH SEGMENTS BATCH S3 UPLOAD ERROR XX]: Previous Task ('dash_segment_video') Failed.\nFail Reason: {error}\nSkipping the - {upload_dash_segments_to_s3.name} Task."
        )
        return preprocessing_result

    try:


        video_file_extention = preprocessing_result["video_file_extention"]
        video_filename_without_extention = preprocessing_result[
            "video_filename_without_extention"
        ]

        if video_file_extention == ".mp4":
            local_video_main_segments_dir_path = preprocessing_result[
                "mp4_segment_files_output_dir"
            ]
        elif video_file_extention == ".mov":
            local_video_main_segments_dir_path = preprocessing_result[
                "mov_segment_files_output_dir"
            ]

        logger.info(
            f"\n=> MAIN DASH SEGMENTS BATCH S3 UPLOAD STARTED]: DASH Segments Batch Creation for S3 Upload Stared for Directroy: {local_video_main_segments_dir_path}."
        )

        # S3 File Structure: vod-media/UUID__rain-calm-video/extention/all-segment-files and mpd file
        video_file_extention_without_dot = video_file_extention.split(".")[
            1
        ]  # "mp4" or "mov" part from ".mp4" or ".mov"

        s3_main_file_path = f"{settings.DASH_S3_FILE_ROOT}/{video_filename_without_extention}/{video_file_extention_without_dot}"

        segment_batchs = []
        current_batch = []
        segment_batch_size = 10

        for root, dirs, files in os.walk(local_video_main_segments_dir_path):
            for file in files:
                local_single_segment_path = os.path.join(root, file)
                s3_file_path = os.path.join(s3_main_file_path, file)

                # Tuple[0]: local single segment file path.
                # Tuple[1]: s3 file path for s3 bucket
                current_batch.append((local_single_segment_path, s3_file_path))

                if len(current_batch) >= segment_batch_size:
                    segment_batchs.append(current_batch)
                    current_batch = []

        # If the segment_batch size is < 10
        if current_batch:
            segment_batchs.append(current_batch)

        #  creating group and chord to make sure upload process is completed before the  "cleanup_local_files_and_segments" task run in the chain.
        segment_upload_group = group(
            upload_segment_batch_to_s3_sub_task.s(single_batch)
            for single_batch in segment_batchs
        )

        # cleanup task is a callback.
        setment_upload_chord = chord(
            segment_upload_group,
            segment_upload_group_callback_and_cleanup.s(preprocessing_result),
        )

        setment_upload_chord.apply_async()

        preprocessing_result["status"] = "success"
        preprocessing_result["upload_dash_segments_to_s3_error"] = (
            "group for segment upload created. awating to upload segments to s3. "
        )

        return preprocessing_result

    except Exception as e:
        logger.error(
            f"\n[XX MAIN DASH SEGMENTS BATCH S3 UPLOAD ERROR XX]: Unexpected Error Occurred.\nException: {str(e)}"
        )
        preprocessing_result["status"] = "failure"
        preprocessing_result["upload_dash_segments_to_s3_error"] = (
            "unexpected error occurred during creating group and chord for s3 batch segments creation."
        )
        preprocessing_result["error"] = str(e)
        return preprocessing_result


# S3 Upload Chord callback. Only executes after the header tasks i.e. segment upload to s3 are completed.
@shared_task
def segment_upload_group_callback_and_cleanup(results, preprocessing_result):

    # Checkpoint for S3 Upload
    logger.info(
        f"\n\n[=> SEGMENTS UPLOAD S3 GROUP CHORD CALLBACK]: Validating Segments Upload Status."
    )

    if all(result == "success" for result in results):
        logger.info(
            f"\n[ => SEGMENTS UPLOAD S3 GROUP CHORD CALLBACK]: SEGMENTS BATCH S3 UPLOAD SUCCESS: Task - {upload_dash_segments_to_s3.name} - is successfull.\nCallback: {segment_upload_group_callback_and_cleanup.name}"
        )
        preprocessing_result["status"] = "success"
        preprocessing_result["upload_status"] = (
            "upload success initialize for cleanup files"
        )
    else:
        logger.error(
            f"\n[XX SEGMENTS UPLOAD S3 GROUP CHORD CALLBACK XX]: SEGMENTS BATCH S3 UPLOAD ERROR: Task - {upload_dash_segments_to_s3.name} - Some segments failed to upload.\nCallback: {segment_upload_group_callback_and_cleanup.name}."
        )
        preprocessing_result["status"] = "failure"
        preprocessing_result["error"] = "upload partial failure"
        preprocessing_result["upload_error"] = (
            "some segments failed to upload. initialized for cleanup"
        )

    logger.info(
        f"\n\n[=> SEGMENTS UPLOAD S3 GROUP CHORD CALLBACK]: Starting Cleaning Up Local Files.]"
    )

    # To delete the local raw video file
    local_video_path_with_extention = preprocessing_result[
        "local_video_path_with_extention"
    ]

    # To delete the segments and the segment dire
    if preprocessing_result["video_file_extention"] == ".mp4":
        local_segments_path_dir = preprocessing_result["mp4_segment_files_output_dir"]
    elif preprocessing_result["video_file_extention"] == ".mov":
        local_segments_path_dir = preprocessing_result["mov_segment_files_output_dir"]

    try:
        if local_video_path_with_extention and os.path.isfile(
            local_video_path_with_extention
        ):
            os.remove(local_video_path_with_extention)

            preprocessing_result["status"] = "success"
            preprocessing_result["file_cleanup_status"] = (
                f"video file: {local_video_path_with_extention} - is deleted. s3 upload completed."
            )

            logger.info(
                "\n[=> SEGMENTS UPLOAD S3 GROUP CHORD CALLBACK]: Video File Cleanup Success."
            )

    except (FileNotFoundError, Exception) as e:
        logger.error(
            f"""\n[XX SEGMENTS UPLOAD S3 GROUP CALLBACK/CLEANUP ERROR XX]: The file: {local_video_path_with_extention} does not exist.\n
            Callback: {segment_upload_group_callback_and_cleanup.name}.\nException: {str(e)}
            """
        )

        preprocessing_result["status"] = "failure"
        preprocessing_result["error"] = "video file cleanup failed."
        preprocessing_result["file_cleanup_error"] = (
            f"video file: {local_video_path_with_extention} - deletion failed. Error: {str(e)}. s3 upload completed."
        )

    # Delete the segment files and the dir.
    try:
        for root, dirs, files in os.walk(local_segments_path_dir):
            for file in files:
                os.remove(os.path.join(root, file))
        os.rmdir(local_segments_path_dir)

        preprocessing_result["status"] = "success"
        preprocessing_result["segment_cleanup_status"] = (
            "segment files cleanup success. s3 upload completed."
        )

        logger.info(
            "\n[=> SEGMENTS UPLOAD S3 GROUP CHORD CALLBACK]: Segment Files Cleanup Success."
        )

    except (FileNotFoundError, Exception) as e:
        logger.error(
            f"""\n\n[XX SEGMENTS UPLOAD S3 GROUP CALLBACK/CLEANUP ERROR XX]: The file: {local_video_path_with_extention} does not exist.\n
                 Callback: {segment_upload_group_callback_and_cleanup.name} .\nException: {str(e)}
            """
        )
        preprocessing_result["status"] = "failure"
        preprocessing_result["error"] = "segment_files_cleanup_error"
        preprocessing_result["segment_cleanup_error"] = (
            f"some segments deletion failed. Error: {str(e)}. s3 upload completed."
        )
        
    return preprocessing_result
