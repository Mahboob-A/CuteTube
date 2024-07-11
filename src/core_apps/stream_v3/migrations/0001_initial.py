# Generated by Django 4.2.9 on 2024-07-10 12:29

import autoslug.fields
from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="VideoMetaData",
            fields=[
                (
                    "pkid",
                    models.BigAutoField(
                        editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "id",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "original_video_title",
                    models.CharField(
                        max_length=220, verbose_name="Original Video Metadata Title"
                    ),
                ),
                ("title", models.CharField(max_length=220, verbose_name="Video Title")),
                (
                    "slug",
                    autoslug.fields.AutoSlugField(
                        always_update=True,
                        editable=False,
                        populate_from="title",
                        unique=True,
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True, null=True, verbose_name="Video Description"
                    ),
                ),
                ("duration", models.DurationField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Video Meta Data",
                "verbose_name_plural": "Videos Meta Data",
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["title"], name="stream_v3_v_title_96c1ce_idx")
                ],
            },
        ),
    ]