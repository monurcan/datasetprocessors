# This script converts image frames to a video.
# bash frames_to_video.sh IMAGES_FOLDER IMG_EXT VIDEO_PATH FRAME_RATE
# Example:
# bash frames_to_video.sh /raid/KaraGAG/Fujinon_Trains/outputs/base_onurcan/501 png /raid/KaraGAG/Fujinon_Trains/outputs/base_onurcan/501.mp4 25

cat $(find $1 -maxdepth 1 -name "*.$2" | sort -V) | ffmpeg -framerate $4 -i - -c:v libx264 -crf 28 -pix_fmt yuv420p $3
