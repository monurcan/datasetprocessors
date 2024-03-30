import argparse
import json
import math
import os
import pathlib
import shutil
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import pandas as pd
from lxml import etree
from tqdm import tqdm
from wcmatch.pathlib import Path

"""
    This script remappes the YOLO class IDs to the new ones. Useful for Roboflow datasets.

    Example usage:
        python remap_yolo.py --folder /mnt/RawInternalDatasets/KaraGAG/MWIR/FromWeb/Roboflow/thermal_cow_deneme \
            --labels_order "Vehicle=0, Person=1, Animal=2, Herd=3, Antitank=4" \
            --remap "0>Person, 1>Herd, 2>delete, 3>ignore, 4>Herd"

    This will
        remap class ID 0 to 1 (Person)
        remap class ID 1 to 3 (Herd)
        delete the images containing BBs with class ID 2
        delete the BBs with class ID 3
        remap class ID 4 to 3 (Herd)

    The old annotations will be carried to 'labels_false' folder.
    The deleted images will be carried to 'images_deleted' folder, and, their annotations will be carried to 'labels_deleted'.
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='YOLO class ID remapper.')
    parser.add_argument('--folder', required=True, type=str,
                        help="Where the data is stored. The 'images' will be replaced by 'labels' to find the annotations.")
    parser.add_argument('--labels_order', default="Vehicle=0, Person=1, Animal=2, Herd=3, Antitank=4", type=str,
                        help="Specify the label order for integer class ID mapping, example: 'Vehicle=0, Person=1, Animal=2, Herd=3, Antitank=4'.")
    parser.add_argument('--remap', required=True, type=str,
                        help="Specify in the form of 'current_id1>new_label1, current_id2>new_label2, ...'. Specify new_label as 'delete' to delete such images. Specify new_label as 'ignore' to delete such bounding boxes.")
    args = parser.parse_args()

    # Recursively get all the images
    img_files = list(Path(args.folder).rglob(
        ['*.png', '*.PNG', '*.jpg', '*.JPG', '*.jpeg', '*.JPEG', '*.bmp', '*.BMP']))

    # Parse the remap argument
    remap_dict = dict([one_remapping.strip().split(">")
                      for one_remapping in args.remap.split(',')])

    # Parse the labels_order argument
    label_dict = dict([label.strip().split("=")
                      for label in args.labels_order.split(',')])
    label_dict['delete'] = 'delete'
    label_dict['ignore'] = 'ignore'

    # Update remap_dict with labels_order
    remap_dict_final = {current_id: label_dict[new_label]
                        for current_id, new_label in remap_dict.items()}

    # Move old annotations to 'labels_false' folder
    img_folders = {str(img.parent) for img in img_files}
    for img_folder in img_folders:
        label_folder_old = img_folder.replace('images', 'labels')
        label_folder_new = img_folder.replace('images', 'labels_false')
        shutil.move(label_folder_old, label_folder_new)
        os.makedirs(label_folder_old, exist_ok=True)

    # Create 'images_deleted' and 'images_deleted_labels' folders
    for img_folder in img_folders:
        images_deleted_folder = img_folder.replace('images', 'images_deleted')
        labels_deleted_folder = img_folder.replace('images', 'labels_deleted')
        os.makedirs(images_deleted_folder, exist_ok=True)
        os.makedirs(labels_deleted_folder, exist_ok=True)

    # Traverse all the images
    for img in tqdm(img_files):
        img_path = str(img)
        img_ext = str(img.suffix)

        old_label_path = img_path.replace(
            'images/', 'labels_false/').replace(img_ext, '.txt')
        remapped_label_path = img_path.replace(
            'images/', 'labels/').replace(img_ext, '.txt')

        try:
            with open(remapped_label_path, 'w') as f:
                for line in open(old_label_path, "r"):
                    values = line.split(" ")
                    label_new = remap_dict_final[values[0]]

                    if label_new == 'delete':
                        deleted_img_path = img_path.replace(
                            'images/', 'images_deleted/')
                        shutil.move(img_path, deleted_img_path)
                        deleted_label_path = remapped_label_path.replace(
                            'labels/', 'labels_deleted/')
                        shutil.move(remapped_label_path, deleted_label_path)
                        break
                    elif label_new == 'ignore':
                        continue
                    else:
                        f.write(
                            f"{label_new} {values[1]} {values[2]} {values[3]} {values[4]}")
        except OSError as e:
            print(f"Not found: {remapped_label_path}")
