import argparse
import json
import os
import time
from time import sleep

import cv2
from natsort import natsorted
from tqdm import tqdm


def list_files(path, ext):
    files_ = []
    for root, _, files in os.walk(path):
        for f in files:
            if f.lower().endswith(ext):
                files_.append(os.path.join(root, f))

    return natsorted(files_)


parser = argparse.ArgumentParser(description="Test YOLO data.")
parser.add_argument("--im_folder", required=True)
parser.add_argument("--coco_labels")
parser.add_argument("--labels", default="ida,boat,ship,floatsam,sail,other")
parser.add_argument("--wait", type=int, default=0)
args = parser.parse_args()

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif")
image_files = list_files(args.im_folder, IMAGE_EXTENSIONS)

label_names = args.labels.split(",")

print("onurcan")
with open(args.coco_labels, "r", encoding="utf-8", errors="ignore") as json_data:
    for line in json_data:
        print(line)
    coco_labels = json.load(json_data, strict=False)
print(coco_labels)

asds

cv2.namedWindow("YOLO Visualizer", cv2.WINDOW_NORMAL)

skip_counter = 0

for idx, image in enumerate(tqdm(image_files)):
    if skip_counter > 0:
        skip_counter -= 1
        time.sleep(0.015)
        continue

    frame = cv2.imread(image)

    coordinates = []

    lines = open(txt_path, "r")

    with lines:
        for line in lines:
            coordinates = line.rstrip("\n").split(" ")
            idx = coordinates[0]

            hT, wT, cT = frame.shape
            x1, y1, w2, h2 = (
                float(coordinates[1]),
                float(coordinates[2]),
                float(coordinates[3]),
                float(coordinates[4]),
            )
            # print(x1,y1,w2,h2)
            w, h = int(w2 * wT), int(h2 * hT)
            x, y = int((x1 * wT) - w / 2), int((y1 * hT) - h / 2)

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
            cv2.putText(
                frame,
                label_names[int(idx)],
                (x, y + 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (128, 0, 255),
                2,
            )

        if not_found:
            continue

        cv2.putText(
            frame,
            image.split("/")[-1],
            (30, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (255, 255, 255),
            0,
        )
        cv2.imshow("YOLO Visualizer", frame)
        key = cv2.waitKey(args.wait)

        if key == ord("q"):
            break
        elif key == ord("v"):
            skip_counter = 25
