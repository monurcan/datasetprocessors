import argparse
import os
from pathlib import Path

import cv2
from tqdm import tqdm

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Image inpainter.')

    parser.add_argument('--folder', required=True, type=str,
                        help="Where the images are stored")
    parser.add_argument('--dest_folder', required=True, type=str,
                        help="Where to save the inpainted images")
    parser.add_argument('--img_ext', default="png", type=str,
                        help="Image extension")
    parser.add_argument('--mask_path', required=True, type=str,
                        help="Paint the inpainted regions black")
    args = parser.parse_args()

    os.makedirs(args.dest_folder, exist_ok=True)

    mask = cv2.imread(args.mask_path, 0)
    _, mask = cv2.threshold(mask, 128, 255, cv2.THRESH_BINARY_INV)

    for path in tqdm(sorted(Path(args.folder).rglob('*.'+args.img_ext))):
        img = cv2.imread(str(path))
        inpainted = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)
        cv2.imwrite(os.path.join(args.dest_folder, path.name), inpainted)
