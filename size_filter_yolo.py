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
    This script elects the small YOLO bounding boxes.

    Example usage:
        python size_filter_yolo.py --folder /mnt/RawInternalDatasets/KaraGAG/MWIR/FromWeb/Roboflow/thermal_cow_deneme \
            --labels_order "Vehicle=0, Person=1, Animal=2, Herd=3, Antitank=4" \
            --filter "Person|0.5x0.6|b|i, Vehicle|0.03x0.01|s|d"

    This will
        ignore the Person labels with width larger than 0.5 or height larger than 0.6.
        delete the images containing Vehicle labels with width smaller than 0.03 or height smaller than 0.01.
    
    The old annotations will be carried to 'labels_false_filtered' folder.
    The deleted images will be carried to 'images_deleted_filtered' folder, and, their annotations will be carried to 'labels_deleted_filtered'.
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='YOLO label size filter.')
    parser.add_argument('--folder', required=True, type=str,
                        help="Where the data is stored. The 'images' will be replaced by 'labels' to find the annotations.")
    parser.add_argument('--labels_order', default="Vehicle=0, Person=1, Animal=2, Herd=3, Antitank=4", type=str,
                        help="Specify the label order for integer class ID mapping, example: 'Vehicle=0, Person=1, Animal=2, Herd=3, Antitank=4'.")
    parser.add_argument('--filter', required=True, type=str,
                        help="Specify in the form of '[label1]|[percentage_threshold1]|[b/s]|[i/d], [label2]|[percentage_threshold2]|[b/s]|[i/d], ...'. Delete big or small ones: [b/s]. Ignore or delete the image: [i/d].")
    args = parser.parse_args()

    # Recursively get all the images
    img_files = list(Path(args.folder).rglob(
        ['*.png', '*.PNG', '*.jpg', '*.JPG', '*.jpeg', '*.JPEG', '*.bmp', '*.BMP']))

    # Parse the filter argument
    filter_ = [one_filter.strip().split("|")
               for one_filter in args.filter.split(',')]

    # Parse the labels_order argument
    label_dict = dict([label.strip().split("=")
                      for label in args.labels_order.split(',')])

    # Update filter_dict with labels_order
    filter_dict_final = {label_dict[filter_info[0]]: (*(filter_info[1].strip().split("x")), filter_info[2], filter_info[3])
                         for filter_info in filter_}

    # Move old annotations to 'labels_false' folder
    img_folders = {str(img.parent) for img in img_files}
    for img_folder in img_folders:
        label_folder_old = img_folder.replace('images', 'labels')
        label_folder_new = img_folder.replace('images', 'labels_false_filtered')
        shutil.move(label_folder_old, label_folder_new)
        os.makedirs(label_folder_old, exist_ok=True)

    # # Create 'images_deleted' and 'images_deleted_labels' folders
    for img_folder in img_folders:
        images_deleted_folder = img_folder.replace('images', 'images_deleted_filtered')
        labels_deleted_folder = img_folder.replace('images', 'labels_deleted_filtered')
        os.makedirs(images_deleted_folder, exist_ok=True)
        os.makedirs(labels_deleted_folder, exist_ok=True)

    # # Traverse all the images
    for img in tqdm(img_files):
        img_path = str(img)
        img_ext = str(img.suffix)

        old_label_path = img_path.replace(
            'images/', 'labels_false_filtered/').replace(img_ext, '.txt')
        filtered_label_path = img_path.replace(
            'images/', 'labels/').replace(img_ext, '.txt')

        try:
            with open(filtered_label_path, 'w') as f:
                for line in open(old_label_path, "r"):
                    values = line.split(" ")
                    filter_info = filter_dict_final.get(
                        values[0], ('99', '99', 'b', 'i'))

                    isFiltered = False
                    if (filter_info[2] == 'b' and (float(values[3]) > float(filter_info[0]) or float(values[4]) > float(filter_info[1]))) or (filter_info[2] == 's' and (float(values[3]) < float(filter_info[0]) or float(values[4]) < float(filter_info[1]))):
                        isFiltered = True

                    if not isFiltered:
                        f.write(
                            f"{values[0]} {values[1]} {values[2]} {values[3]} {values[4]}")
                        continue

                    if filter_info[3] == 'i':
                        continue
                    elif filter_info[3] == 'd':
                        deleted_img_path = img_path.replace(
                            'images/', 'images_deleted_filtered/')
                        shutil.move(img_path, deleted_img_path)
                        deleted_label_path = filtered_label_path.replace(
                            'labels/', 'labels_deleted_filtered/')
                        shutil.move(filtered_label_path, deleted_label_path)
                        break
                    else:
                        print("--filter flag should contain i or d!")

        except OSError as e:
            print(f"Not found: {filtered_label_path}")
