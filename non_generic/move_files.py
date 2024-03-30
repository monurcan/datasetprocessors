import shutil
from pathlib import Path

from natsort import natsorted

image_folder_path = '/mnt/RawInternalDatasets/KaraGAG/Xenics/Old/v5/yolo_thermal_data-v5.5_27.05.22_copied_imgs/train/images'
img_paths = natsorted(list(Path(image_folder_path).rglob('*.jpeg')))

# print(img_paths)

for img_path in img_paths:
    img_path = str(img_path)
    label_path = img_path.replace(
        '.jpeg', '.txt').replace('/images/', '/labels/')

    new_label_path = label_path.replace(
        '/train/', '/flir_adas/')
    new_img_path = img_path.replace('/train/', '/flir_adas/')

    shutil.move(img_path, new_img_path)
    shutil.move(label_path, new_label_path)
