# DOWNLOAD_DIR="/raid/KaraGAG/MWIR/CVAT_new"
DOWNLOAD_DIR="/raid/KaraGAG/Fujinon/CVAT_new"
TASK_ID=$1

###########################################################################################
# PARSER OPTIONS, YOU CAN SET THEM TO "" TO IGNORE THAT OPERATION

# MWIR LAST SETTINGS
# CROP_BY="73,58,1207,963"
# GUI_MASK_PATH="/raid/KaraGAG/parsers_mnt/inpaint_masks/mwir_newer.jpg"
# PROCESS_THERMAL=true

# FUJINON LAST SETTINGS
CROP_BY=""
GUI_MASK_PATH="/raid/KaraGAG/parsers_mnt/inpaint_masks/fujinon_very_very_new.jpg"
PROCESS_THERMAL=false

###########################################################################################
PARSERS_PATH=/raid/KaraGAG/parsers_mnt/

# CVAT CONNECTION
CVAT_USERNAME="monurcan"
CVAT_PASSWORD="iammemo55"
CVAT_AUTH="--auth ${CVAT_USERNAME}:${CVAT_PASSWORD} --server-host 192.168.1.26 --server-port 8080"

###########################################################################################
cd "$DOWNLOAD_DIR"

# If $TASK_ID folder already exists, ask whether delete it or not
if [ -d "$TASK_ID" ]; then
    read -p "The folder $TASK_ID already exists. Do you want to delete it? [y/n] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$TASK_ID"
    else
        echo "Aborting..."
        exit 1
    fi
fi

mkdir "$TASK_ID"
cd "$TASK_ID"

if cvat-cli $CVAT_AUTH dump --format "YOLO 1.1" "$TASK_ID" "output_${TASK_ID}.zip" --with-images True; then
    unzip "output_${TASK_ID}.zip"
    rm "output_${TASK_ID}.zip"
    mv obj_train_data images
    mkdir labels
    mv images/*.txt labels

    # Find the extension
    files=("images"/*)
    shopt -s extglob
    first_file="${files[0]}"
    extension="${first_file##*.}"
    echo "The files in the folder have the extension: $extension"
    shopt -u extglob

    # Rename folders
    mv images images_first
    mv labels labels_first
    current_image_path="images_first"
    current_label_path="labels_first"

    # Crop images
    if [ -n "$CROP_BY" ]; then
        echo "Cropping images..."
        python3 "$PARSERS_PATH/crop_images_with_yolo_labels.py" --folder "$PWD/$current_image_path" --img_ext "$extension" --size "$CROP_BY"
        current_image_path="images_cropped"
        current_label_path="labels_cropped"
    else
        echo "No cropping..."
    fi

    # Apply GUI mask
    if [ -n "$GUI_MASK_PATH" ]; then
        echo "Applying GUI mask..."
        python3 "$PARSERS_PATH/inpaint_images.py" --folder "$current_image_path" --dest_folder images_cropped_inpainted --img_ext "$extension" --mask_path "$GUI_MASK_PATH"
        current_image_path="images_cropped_inpainted"
    else
        echo "No GUI mask..."
    fi

    # Process thermal images
    if [ "$PROCESS_THERMAL" = true ]; then
        echo "Processing thermal images..."
        python3 "$PARSERS_PATH/process_thermal.py" --folder "$current_image_path" --img_ext "$extension"
        current_image_path="images_cropped_inpainted"
    else
        echo "No thermal processing..."
    fi

    # Rename folders
    mv $current_image_path images
    mv $current_label_path labels

    echo "Processing completed... Now investigate the dataset with: "
    echo "python3 ${PARSERS_PATH}/yolo_visualizer.py --im_folder ${DOWNLOAD_DIR}/${TASK_ID}/images --txt_folder ${DOWNLOAD_DIR}/${TASK_ID}/labels"
else
    echo "Failed to download the dataset"
fi
