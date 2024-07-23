from django.db import models
from django.utils.translation import gettext_lazy as _

from autoslug import AutoSlugField

from core_apps.common.models import IDTimeStampModel


class VideoMetaDataDRMV4(IDTimeStampModel):
    """Metadata class for Videos that are uploaded to the S3."""

    custom_video_title = models.CharField(
        verbose_name=_("Custom Video Metadata Title (UUID__title)"), max_length=220
    )
    title = models.CharField(verbose_name=_("Video Title"), max_length=220)
    slug = AutoSlugField(populate_from="title", always_update=True, unique=True)

    # The local temporary manifest.mpd file path is: BASE_DIR/local-vod-segments-temp/UUID__rain-bg-video/mov/manifest.mpd
    # The S3 manifest.mpd file path is: vod-media/UUID__rain-calm-video/extention/manifest.mpd
    # EX: f"https://{s3_bucket_name}.s3.amazonaws.com/vod-media/{video_name}/extention/manifest.mpd"
    mp4_s3_mpd_url = models.CharField(
        verbose_name=_("S3 URL for mp4 MPD file."),
        max_length=255,
        null=True,
        blank=True,
    )

    mov_s3_mpd_url = models.CharField(
        verbose_name=_("S3 URL for mov MPD file."),
        max_length=255,
        null=True,
        blank=True,
    )

    mp4_gcore_cdn_mpd_url = models.CharField(
        verbose_name=_("MP4: Gcore CDN URL file."),
        max_length=255,
        null=True,
        blank=True,
    )

    mov_gcore_cdn_mpd_url = models.CharField(
        verbose_name=_("MOV: Gcore CDN URL MPD file."),
        max_length=255,
        null=True,
        blank=True,
    )

    description = models.TextField(
        verbose_name=_("Video Description"), blank=True, null=True
    )
    duration = models.DurationField(null=True, blank=True)

    class Meta:
        verbose_name = _("Video Meta Data DRM V4")
        verbose_name_plural = _("Videos Meta Data DRM V4")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["title"])]

    @property
    def video_title(self):
        return self.title

    def __str__(self) -> str:
        return self.title
