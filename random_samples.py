import argparse
import json
import math
import os
import pathlib
import random
import shutil
import xml.etree.ElementTree as ET
import zipfile

import cv2
import numpy as np
import pandas as pd
import yaml
from lxml import etree
from wcmatch.pathlib import Path

"""
    This script gets random samples from a given .yaml file for each dataset.
    
    Example usage:
        python generate_stats.py --input_yaml "" --output_folder ""
"""

# img_files = list(Path(args.folder).rglob(
#     ['*.png', '*.PNG', '*.jpg', '*.JPG', '*.jpeg', '*.JPEG', '*.bmp', '*.BMP']))
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Random dataset sampler.')

    parser.add_argument('--input_yaml', required=True, type=str,
                        help=".yaml file used for YOLO training")
    parser.add_argument('--output_folder', required=True, type=str,
                        help="Where to save the sampled annotations")
    parser.add_argument('--num_samples', type=int, default=3)
    args = parser.parse_args()

    os.makedirs(args.output_folder, exist_ok=True)

    yaml_file = yaml.safe_load(Path(args.input_yaml).read_text())
    all_datasets = yaml_file['train']+yaml_file['val']
    label_names = yaml_file['names']

    for dataset_index, usedset in enumerate(all_datasets):
        img_files = list(Path(usedset).glob(
            ['*.png', '*.PNG', '*.jpg', '*.JPG', '*.jpeg', '*.JPEG', '*.bmp', '*.BMP']))
        img_files = random.sample(img_files, min(
            len(img_files), args.num_samples))

        print(usedset)

        for img in img_files:
            img_pth = str(img)
            img_ext = str(img.suffix)

            sample_img = cv2.imread(img_pth)
            hT, wT, cT = sample_img.shape
            # print(hT, wT)

            img_name = str(dataset_index) + img_pth.replace('/', '__')

            txt_path = img_pth.replace(
                'images/', 'labels/').replace(img_ext, '.txt')

            try:
                lines = open(txt_path, "r")

                for line in lines:
                    coordinates = line.rstrip('\n').split(' ')
                    idx = coordinates[0]

                    x1, y1, w2, h2 = float(coordinates[1]), float(
                        coordinates[2]), float(coordinates[3]), float(coordinates[4])

                    w, h = int(w2 * wT), int(h2 * hT)
                    x, y = int((x1 * wT) - w / 2), int((y1 * hT) - h / 2)
                    cv2.rectangle(sample_img, (x, y),
                                  (x+w, y+h), (0, 255, 255), 2)
                    cv2.putText(sample_img, label_names[int(
                        idx)], (x, y+10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (128, 0, 255), 2)
            except OSError:
                print("Could not open/read file:", txt_path)

            cv2.imwrite(os.path.join(args.output_folder, img_name), sample_img)
