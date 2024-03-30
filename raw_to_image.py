import argparse
import os
from pathlib import Path

import cv2
import numpy as np
from tqdm import tqdm

# KARAGAG:
# XENICS    : 640x480
# FUJINON   : 1920x1080
# MWIR      : 570X456
# IMPERIX   : 6464X4860

def convert_raw_to_opencv(file_path, width, height):
    with open(file_path, "rb") as rawimg:
        # Read the raw image as uint16 (two bytes per pixel).
        bayer_im = np.fromfile(rawimg, np.uint16, width *
                               height).reshape(height, width)

        # The 12 bits of each pixel are stored in the upper 12 bits of every uint16 element.
        # The lower 4 bits of the uint16 element are zeros.
        # <--- 16 bits -->
        # ************0000
        # <-12 bits -><4->
        #    data     zeros

        # Apply Demosacing.
        # It look like COLOR_BAYER_BG2BGR gives the best result, but it hard to tell from the given input.
        # The result is BGR format with 16 bits per pixel range [0, 2^16-1].
        bgr = cv2.cvtColor(bayer_im, cv2.COLOR_BAYER_BG2BGR)

        return bgr


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Raw Bayer CFA image converter.')

    parser.add_argument('--folder', required=True, type=str,
                        help="Where the images are stored")
    parser.add_argument('--dest_folder', required=True, type=str,
                        help="Where to save the images")
    parser.add_argument('--img_ext', default="png", type=str,
                        help="Image extension to save")
    parser.add_argument('--width', required=True, type=int,
                        help="Image width")
    parser.add_argument('--height', required=True, type=int,
                        help="Image height")
    args = parser.parse_args()

    os.makedirs(args.dest_folder, exist_ok=True)

    for path in tqdm(sorted(Path(args.folder).glob('*'))):
        if not path.is_file():
            continue

        opencv_img = convert_raw_to_opencv(path, args.width, args.height)

        cv2.imwrite(os.path.join(args.dest_folder, path.name) +
                    "."+args.img_ext, opencv_img)
