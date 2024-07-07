import os
import logging

from django.shortcuts import render
from django.conf import settings
from django.http import (
    FileResponse,
    HttpResponse,
    HttpResponseNotFound,
    StreamingHttpResponse,
)
from django.views.decorators.http import require_GET

from rest_framework import status

from wsgiref.util import FileWrapper


logger = logging.getLogger(__name__)


@require_GET
def stream_video(request):
    # video_path = os.path.join(os.path.dirname(__file__), "..", "..", "rain-bg-vid.mp4")
    video_path = os.path.join(settings.BASE_DIR, "rain-thunder-bg-vid.mp4")

    #     print('\nvideo_path', video_path)

    range_header = request.META.get("HTTP_RANGE", "").strip()

    try:
        print()
        file_size = os.path.getsize(video_path)

        #  8 KB (in bytes)
        chunk_size = 8192

        response = HttpResponse(status=206)
        response["Content-Type"] = "video/mp4"
        response["Accept-Ranges"] = "bytes"
        # response.write(str('ok'))

        if range_header:
            ranges = range_header.replace("bytes=", "").split("-")
            start_bytes = int(ranges[0]) if ranges[0] else 0
            end_bytes = int(ranges[1]) if ranges[1] else file_size - 1
            print("start: ", start_bytes)
            print("end: ", end_bytes)

            # handling invalid seek or range
            if (
                start_bytes > end_bytes
                or start_bytes < 0
                or start_bytes >= file_size
                or end_bytes >= file_size
            ):
                return HttpResponse(
                    status=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                    headers={"Content-Range": f"bytes */{file_size}"},
                )
            #     print('start: ', start_bytes)
            #     print('end: ', end_bytes)

            response["Content-Range"] = f"bytes {start_bytes}-{end_bytes}/{file_size}"
            response["Content-Length"] = str(end_bytes - start_bytes + 1)
        else:
            response["Content-Length"] = str(file_size)

        #  handling both cases, range or default streaming (default is not seeking the video, streaming from the beginning)
        with open(video_path, "rb") as video_file:
            if range_header:
                video_file.seek(start_bytes)

            # streaming the chunks
            while True:
                chunk = video_file.read(chunk_size)

                if not chunk:
                    break
                response.write(chunk)
        # print('response: ', response)

        logger.info("\n\nVideo chunk write completed in response body.")
        return response

    except FileNotFoundError:
        return HttpResponseNotFound("Video file not found.")


###############################################################
# This view doesn't work as expected. It only streams the first chunk, hence, below I have taken different approach
# that writes the chunks in the response body. Note that FileResponse inheris the StreamingHttpResponse
# @require_GET
# def stream_video_1(request):
# #     print('requst method: ', request.method)
#     video_path = os.path.join(settings.BASE_DIR, "rain-bg-vid.mp4")
#     print("video path: ", video_path)

#     try:
#         file_size = os.path.getsize(video_path)
#         print("file size: ", file_size)

#         range_header = request.META.get("HTTP_RANGE", "").strip()

#         print("range header: ", range_header)

#         if range_header:
#             ranges = range_header.replace("bytes=", "").split("-")
#             print("ranges: ", ranges)

#             start_bytes = int(ranges[0]) if ranges[0] else 0
#             end_bytes = int(ranges[1]) if ranges[1] else file_size - 1

#             if start_bytes >= file_size:
#                 return HttpResponse(
#                     status=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
#                     headers={"Content-Range": f"bytes */{file_size}"},
#                 )
#             chunk_size = end_bytes - start_bytes + 1

#             response = FileResponse(
#                 FileWrapper(open(video_path, "rb")),
#                 content_type="video/mp4",
#                 status=206,
#                 as_attachment=False,
#             )

#             response["Accept-Ranges"] = "bytes"
#             response["Content-Length"] = str(chunk_size)
#             response["Content-Range"] = f"bytes {start_bytes}-{end_bytes}/{file_size}"
#             return response

#     except FileNotFoundError as e:
#         return HttpResponseNotFound("Video file not found")
