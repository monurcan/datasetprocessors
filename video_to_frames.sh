# This script converts an input video to png frames.
# bash video_to_frames.sh TARGET_VIDEO DESTINATION_FOLDER
# Example usage:
# bash parsers/video_to_frames.sh /mnt/RawInternalDatasets/karagag/kgag_cekim/kgag_cekim_11_11_21/Fujinon/1430HRS/3200m/3200m-insan-termal-kamuflaj-semsiye_h264_crf18.avi /mnt/RawInternalDatasets/karagag/Fujinon/VK/247/images

mkdir $2 &&
    ffmpeg -i $1 \
        -start_number 0 \
        \
        $2'/frame_%06d.png' # -vf fps=1/3 \
