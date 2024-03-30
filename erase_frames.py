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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Erase frames in the input folder which are not in the dest folder.')
    parser.add_argument('--input_folder', required=True, type=str,
                        help="Where the data is stored. Some of them will be erased.")
    parser.add_argument('--dest_folder', required=True, type=str,
                        help="Dest folder. Input folder images that are not in this folder will be erased.")
    args = parser.parse_args()

    # Recursively get all the images
    input_folder_files = set([file.name for file in Path(args.input_folder).glob(
        ['*.png', '*.PNG', '*.jpg', '*.JPG', '*.jpeg', '*.JPEG', '*.bmp', '*.BMP'])])
    dest_folder_files = set([file.name for file in Path(args.dest_folder).glob(
        ['*.png', '*.PNG', '*.jpg', '*.JPG', '*.jpeg', '*.JPEG', '*.bmp', '*.BMP'])])

    different_files = input_folder_files - dest_folder_files

    print(len(input_folder_files))
    print(len(dest_folder_files))
    print(len(different_files))

    for file in different_files:
        file_path = os.path.join(args.input_folder, file)

        if os.path.isfile(file_path):
            os.remove(file_path)
