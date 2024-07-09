import os

from django.shortcuts import render
from django.conf import settings
from django.views.decorators.http import require_GET
from django.http import HttpResponse, HttpResponseNotFound, FileResponse

from rest_framework import status


# WIth direct mpd file 
@require_GET
def serve_dash_mpd_2(request):
    """
    Serve DASH .mpd File
    """
    video_mpd_path = os.path.join(
        settings.DASH_FILE_ROOT, "anime-village-lifestyle-segs", "manifest.mpd"
    )
    if os.path.exists(video_mpd_path):
        return FileResponse(
            open(video_mpd_path, "rb"), content_type="application/dash+xml"
        )
    else:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

# alternate 
@require_GET
def serve_dash_mpd_3(request):
    """
    Serve DASH .mpd File
    """
    video_mpd_path = os.path.join(
        settings.DASH_FILE_ROOT, "anime-village-lifestyle-segs", "manifest.mpd"
    )
    try:
        with open(video_mpd_path, "rb") as video_mpd_file:
            manifest_content = video_mpd_file.read()
        return HttpResponse(manifest_content, content_type="application/dash+xml")
    except FileNotFoundError:
        return HttpResponseNotFound("DASH manifest not found.")


# segment for direct mpd file 
@require_GET
def serve_dash_segment_2(request, segment_name):
    """
    Serve DASH segment files.
    """
    video_segment_path = os.path.join(
        settings.DASH_FILE_ROOT, "anime-village-lifestyle-segs", segment_name
    )
    try:
        return FileResponse(open(video_segment_path, "rb"), content_type="video/mp4")
    except FileNotFoundError:
        return HttpResponseNotFound(
            f"The DASH Segment: {segment_name} not found."
        )


###################################  Writh dynamic directory (NOTE: Not working. CORS error at manifest.mpd although cors is set correctly.)
@require_GET
def serve_dash_mpd(request, video_name):
    '''
    Serve DASH .mpd File 
    '''
    video_mpd_path = os.path.join(
        settings.DASH_FILE_ROOT, f"{video_name}-segs", "manifest.mpd"
    )
    if os.path.exists(video_mpd_path):
        response = FileResponse(
            open(video_mpd_path, "rb"), content_type="application/dash+xml"
        )
        # response["Access-Control-Allow-Origin"] = "http://127.0.01:8000"
        return response
    else:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)


@require_GET
def serve_dash_segment(request, video_name, segment_name):
    '''
    Serve DASH segment files.
    '''
    video_segment_path = os.path.join(
        settings.DASH_FILE_ROOT, f"{video_name}-segs", segment_name
    )
    try:
        return FileResponse(open(video_segment_path, "rb"), content_type="video/mp4")
    except FileNotFoundError:
        return HttpResponseNotFound(
            f"The DASH Segment: {segment_name} of video: {video_name} not found."
        )
