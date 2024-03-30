import os
import shutil
from collections import Counter
from pathlib import Path

from natsort import natsorted

image_folder_path = '/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/Roboflow_New/CattleCounter_BuTemizlenmeli/train/images'
move_path = image_folder_path+'_deleted_augmentations'

os.makedirs(move_path, exist_ok=True)

img_paths = natsorted(list(Path(image_folder_path).rglob('*')))
img_paths_only_image_name_no_aug = [
    img_pth.stem.split('.')[0] for img_pth in img_paths]

img_paths_only_image_name_no_aug_counter = Counter(
    img_paths_only_image_name_no_aug)

for img_pth in img_paths:
    # Remove if its counter is larger than 1 and decrease the corresponding counter
    if img_paths_only_image_name_no_aug_counter[img_pth.stem.split('.')[0]] > 1:
        shutil.move(img_pth, os.path.join(move_path, img_pth.name))
        img_paths_only_image_name_no_aug_counter[img_pth.stem.split('.')[
            0]] -= 1
