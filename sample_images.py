import argparse
import os
import random
import shutil
from pathlib import Path

import cv2
from tqdm import tqdm

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Image sampler. Moves not sampled instances to INPUTFOLDER_notsampled folder.')

    parser.add_argument('--folder', required=True, type=str,
                        help="Where the images are stored")
    parser.add_argument('--sample_percentage', required=True, type=float,
                        help="What percent of the images are retained.")
    parser.add_argument('--img_ext', default="png", type=str,
                        help="Image extension")
    args = parser.parse_args()

    args.sample_percentage = args.sample_percentage / 100

    if args.folder[-1] == '/':
        args.folder = args.folder[:-1]

    shutil.move(args.folder, args.folder+"_notsampled")
    os.makedirs(args.folder, exist_ok=True)

    img_list = sorted(Path(args.folder+"_notsampled").rglob('*.'+args.img_ext))
    sampled_img_list = random.sample(
        img_list, int(len(img_list)*args.sample_percentage))

    for sample in sampled_img_list:
        shutil.move(sample, os.path.join(args.folder, sample.name))
