import argparse
import os
import random
import shutil
from pathlib import Path

import cv2
import numpy as np
from tqdm import tqdm

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Thermal image enhancer.")

    parser.add_argument(
        "--folder", required=True, type=str, help="Where the images are stored"
    )
    parser.add_argument("--img_ext", default="PNG", type=str, help="Image extension")
    args = parser.parse_args()

    if args.folder[-1] == "/":
        args.folder = args.folder[:-1]

    shutil.move(args.folder, args.folder + "_notenhanced")
    os.makedirs(args.folder, exist_ok=True)

    img_list = sorted(Path(args.folder + "_notenhanced").rglob("*." + args.img_ext))

    clahe = cv2.createCLAHE(clipLimit=1.0, tileGridSize=(2, 2))
    kernel_sharp = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    alpha = 1.5
    beta = 1.0 - alpha

    for img_name in tqdm(img_list):
        img = cv2.imread(str(img_name))
        # img = cv2.resize(img, (570, 456), interpolation=cv2.INTER_AREA)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        img = cv2.bilateralFilter(src=img, d=5, sigmaColor=75, sigmaSpace=75)
        img = cv2.filter2D(img, -1, kernel_sharp)
        gaussian_blur = cv2.GaussianBlur(img, (0, 0), 10.0)
        img = cv2.addWeighted(img, alpha, gaussian_blur, beta, 0, img)
        img = clahe.apply(img)

        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        img_save_pth = os.path.join(args.folder, img_name.name)
        # print(img_save_pth)
        res = cv2.imwrite(img_save_pth, img)
