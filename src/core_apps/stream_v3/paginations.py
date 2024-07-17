from rest_framework.pagination import PageNumberPagination


class VideoMetaDataPageNumberPagination(PageNumberPagination):
    """Pagination class for core_apps.stream_v3.models.VideoMetaData"""

    page_size = 10
    page_query_param = "page"
    max_page_size = 25
