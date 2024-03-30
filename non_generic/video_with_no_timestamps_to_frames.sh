# Some recorder buckets don't have timestamps
# This script converts such videos to jpg images

mkdir $2 &&
    cd $2 &&
    mpv --vo=image --sstep=0 $1
