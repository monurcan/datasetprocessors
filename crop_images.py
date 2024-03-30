import argparse
import os
from pathlib import Path

import cv2
from tqdm import tqdm

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Image cropper.')

    parser.add_argument('--folder', required=True, type=str,
                        help="Where the images are stored")
    parser.add_argument('--dest_folder', required=True, type=str,
                        help="Where to save the cropped images")
    parser.add_argument('--img_ext', default="png", type=str,
                        help="Image extension")
    parser.add_argument('--size', required=True, type=str,
                        help="Crop points in (x_tl, y_tl, x_br, y_br) format")
    args = parser.parse_args()

    os.makedirs(args.dest_folder, exist_ok=True)

    crop_points = [int(filter.strip()) for filter in args.size.split(',')]

    for path in tqdm(sorted(Path(args.folder).rglob('*.'+args.img_ext))):
        img = cv2.imread(str(path))
        cropped = img[crop_points[1]:crop_points[3],
                      crop_points[0]:crop_points[2]]
        # cropped = cv2.resize(cropped, (570, 456))
        cv2.imwrite(os.path.join(args.dest_folder, path.name), cropped)
