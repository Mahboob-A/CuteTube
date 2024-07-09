#!/bin/bash

ffmpeg -i anime-village-lifestyle.mp4 \
-map 0 \
-b:v 2400k \
-s:v 1920x1080 \
-c:v libx264 \
-f dash \
-use_template 1 \
-seg_duration 4 \
-init_seg_name init-\$RepresentationID\$.m4s \
-media_seg_name chunk-\$RepresentationID\$-\$Number%05d\$.m4s \
vod-media/anime-village-lifestyle-segs/anime-village-lifestyle.mpd