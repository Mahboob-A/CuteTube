from django.db import models
from django.utils.translation import gettext_lazy as _

from autoslug import AutoSlugField

from core_apps.common.models import IDTimeStampModel


class VideoMetaData(IDTimeStampModel):
    """Metadata class for Videos that are uploaded to the S3."""

    original_video_title = models.CharField(verbose_name=_("Original Video Metadata Title"), max_length=220)
    title = models.CharField(verbose_name=_("Video Title"), max_length=220)
    slug = AutoSlugField(populate_from="title", always_update=True, unique=True)

    description = models.TextField(
        verbose_name=_("Video Description"), blank=True, null=True
    )
    duration = models.DurationField(null=True, blank=True)

    class Meta:
        verbose_name = _("Video Meta Data")
        verbose_name_plural = _("Videos Meta Data")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["title"])]

    @property
    def video_title(self):
        return self.title

    def __str__(self) -> str:
        return self.title
