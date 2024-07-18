#! /bin/sh
#
# Bu sadece root userlardan calisiyor su an, buyuk ihtimal Xauthoritynin izinleriyle fln alakali diger userlardan calismamasi
# Cakisma da olmuyor iki kisi ayni anda calisabiliyor.

# Fix for running GUI programs from within the docker container:
#
# Make xorg disable access control, i.e. let any x client connect to our
# server.
xhost +local:docker

# In order to let the container connect to the pulseaudio server over TCP,
# the module-native-protocol-tcp module must be enabled:
#
# load-module module-native-protocol-tcp

# 172.17.0.1 is the default host ip address of the docker network interface
# (docker0). In case this is changed (e.g. docker container not using NAT
# address) the below env var must of course be updated.
PULSE_SERVER_TCP_ENV="-e PULSE_SERVER=tcp:172.17.0.1:4713"

WORKSPACE_DIR=$(pwd)/..
XSOCK=/tmp/.X11-unix
XAUTH=$HOME/.Xauthority

echo $DISPLAY
# Create the container with all options needed to let a GUI program
# like qtcreator connect to the host xorg server.
# The current user home directory is also mounted directly into the
# container.
# -v /mnt:/mnt \
docker run -it   \
    --gpus all \
    $PULSE_SERVER_TCP_ENV \
    -e XAUTHORITY=${XAUTH} \
    -e NVIDIA_VISIBLE_DEVICES=all \
    -e NVIDIA_DRIVER_CAPABILITIES=all \
    -e PROJECTS_HOME=/root/workspace \
    -e LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH \
    -e PATH=$PATH:/root/workspace/NeuralNetwork/utils/KCons \
    -e PYTHONPATH=$PYTHONPATH:/root/workspace/NeuralNetwork/utils/KCons \
    -e DISPLAY=$DISPLAY \
    -v $XSOCK:$XSOCK:rw \
    -v /mnt:/mnt \
    -v /mnt_ssd:/mnt_ssd \
    -v /ssd_mnt:/ssd_mnt \
    -v /mnt_datasets:/mnt_datasets \
    -v /mnt_hdd:/mnt_hdd \
    -v /hdd_mnt:/hdd_mnt \
    -v /mnt_smb:/mnt_smb \
    -v /nas_karagoz:/nas_karagoz \
    -v /raid:/raid \
    -v $WORKSPACE_DIR:/home/kilavuz_dev/workspace \
    -v $XAUTH:$XAUTH:rw \
    --privileged \
    --network=host \
    --cap-add=CAP_SYS_ADMIN \
    --name $2 \
    $1

docker exec $2 bash -c 'echo "asdasd"'
#    --rm \
