import glob
import os
import sys
from pathlib import Path

import yaml

if len(sys.argv) < 2:
    print("Please specify the dataset.yaml file")
    sys.exit()

input_file = sys.argv[1]

if not os.path.isfile(input_file):
    print("The dataset.yaml specified does not exist")
    sys.exit()

output_folder = sys.argv[2]

organize_type = int(sys.argv[3])
"""
0 means:
Dataset
├── images
│   ├── train
│   │   ├── train0.jpg
│   │   └── train1.jpg
│   ├── val
│   │   ├── val0.jpg
│   │   └── val1.jpg
│   └── test
│       ├── test0.jpg
│       └── test1.jpg
└── labels
    ├── train
    │   ├── train0.txt
    │   └── train1.txt
    ├── val
    │   ├── val0.txt
    │   └── val1.txt
    └── test
        ├── test0.txt
        └── test1.txt
========================
1 means:
├── Dataset
│   ├── train
│   │   ├── images
│   │   │   ├── 1.jpg
│   │   │   ├── abc.png
|   |   |   ├── ....
│   │   ├── labels
│   │   │   ├── 1.txt
│   │   │   ├── abc.txt
|   |   |   ├── ....
│   ├── val
│   │   ├── images
│   │   │   ├── 2.jpg
│   │   │   ├── fram.png
|   |   |   ├── ....
│   │   ├── labels
│   │   │   ├── 2.txt
│   │   │   ├── fram.txt
|   |   |   ├── ....
│   ├── test
│   │   ├── images
│   │   │   ├── img23.jpeg
│   │   │   ├── 50.jpg
|   |   |   ├── ....
│   │   ├── labels
│   │   │   ├── img23.txt
│   │   │   ├── 50.txt
|   |   |   ├── ....
"""

conf = yaml.safe_load(Path(input_file).read_text())

dataset_root = conf["path"]
all_sets = {
    "train": [os.path.join(dataset_root, x) for x in conf["train"]],
    "val": [os.path.join(dataset_root, x) for x in conf["val"]],
    "test": [os.path.join(dataset_root, x) for x in conf["test"]],
}

labels = conf["names"]
IMG_FORMATS = "bmp", "dng", "jpeg", "jpg", "mpo", "png", "tif", "tiff", "webp", "pfm"


def img2label_paths(img_paths):
    # Define label paths as a function of image paths
    # /images/, /labels/ substrings
    sa, sb = f"{os.sep}images{os.sep}", f"{os.sep}labels{os.sep}"
    return [sb.join(x.rsplit(sa, 1)).rsplit(".", 1)[0] + ".txt" for x in img_paths]


file_index = 0
for dataset_type, used_sets in all_sets.items():
    if organize_type == 1:
        new_im_folder = Path(output_folder) / dataset_type / "images"
        new_label_folder = Path(output_folder) / dataset_type / "labels"
    else:
        new_im_folder = Path(output_folder) / "images" / dataset_type
        new_label_folder = Path(output_folder) / "labels" / dataset_type

    new_im_folder.mkdir(parents=True, exist_ok=True)
    new_label_folder.mkdir(parents=True, exist_ok=True)

    for used_set in used_sets:
        if os.path.isdir(used_set):
            im_files = sorted(
                x.replace("/", os.sep)
                for x in glob.glob(str(Path(used_set) / "**" / "*.*"), recursive=True)
                if x.split(".")[-1].lower() in IMG_FORMATS
            )
            label_files = [x for x in img2label_paths(im_files) if os.path.exists(x)]

            # generate symbolic links in new folders
            for im_file, label_file in zip(im_files, label_files):
                new_im_file = new_im_folder / f"{file_index}_{Path(im_file).name}"
                new_label_file = (
                    new_label_folder / f"{file_index}_{Path(label_file).name}"
                )

                if not new_im_file.exists():
                    os.symlink(im_file, new_im_file)

                if not new_label_file.exists():
                    os.symlink(label_file, new_label_file)

                file_index += 1

        else:
            print("not a directory", used_set)
