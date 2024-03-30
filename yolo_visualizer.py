import argparse
import os
import time
from time import sleep

import cv2
from natsort import natsorted
from tqdm import tqdm

"""
    Example usage:
        python yolo_visualizer_as_video.py --im_folder /mnt/RawInternalDatasets/karagag/Fujinon/VK/243/images --txt_folder /mnt/RawInternalDatasets/karagag/Fujinon/VK/243/labels
    
    eğer txt_folder belirtmezsen images -> labels replaceleyip orada arar
    
    find yaparsan istediginden buluyor
    q -> cikis
    v -> 25 frame ileri
    o -> frame sil
    bir sayiya basarsan hepsini ona cevirir
    baska herhangi bir tus -> bir frame ileri
"""


def list_files(path, ext):
    files_ = []
    for root, _, files in os.walk(path):
        for f in files:
            if f.lower().endswith(ext):
                files_.append(os.path.join(root, f))

    return natsorted(files_)


parser = argparse.ArgumentParser(description="Test YOLO data.")
parser.add_argument("--im_folder", required=True)
parser.add_argument("--txt_folder")
parser.add_argument("--labels", default="vehicle,person,animal,herd,antitank,drone")
parser.add_argument("--wait", type=int, default=0)
parser.add_argument("--find", type=int)
parser.add_argument("--depth_folder", type=str)
args = parser.parse_args()

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif")
image_files = list_files(args.im_folder, IMAGE_EXTENSIONS)

label_names = args.labels.split(",")

if args.txt_folder is None:
    args.txt_folder = args.im_folder.replace("images", "labels")

cv2.namedWindow("YOLO Visualizer", cv2.WINDOW_NORMAL)

not_found = False

id_image = 0
while True:
    print(f"{id_image} / {len(image_files)}")

    image = image_files[id_image]

    if args.find is None:
        frame = cv2.imread(image)

    coordinates = []

    txt_path = os.path.splitext(image)[0]

    if args.txt_folder is not None:
        txt_path = os.path.join(args.txt_folder, txt_path.split("/")[-1])

    txt_path += ".txt"

    try:
        lines = open(txt_path, "r").readlines()
        writeifchangeAll = ""

        if args.depth_folder is not None:
            dist_path = os.path.join(args.depth_folder, txt_path.split("/")[-1])
            dist_lines = open(dist_path, "r").readlines()
            if len(lines) != len(dist_lines):
                print("depth and label size mismatch")
                continue
        wT = 1
        for i, line in enumerate(lines):
            coordinates = line.rstrip("\n").split(" ")
            idx = coordinates[0]

            if args.find is not None:
                if idx != str(args.find):
                    not_found = True
                    continue
                else:
                    frame = cv2.imread(image)
                    not_found = False

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

            writeifchangeAll += f"XXX {x1} {y1} {w2} {h2}\n"

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 1)
            cv2.putText(
                frame,
                label_names[int(idx)],
                (x, y - int(30 * hT / 2000)),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.3 * hT / 2000,
                (128, 0, 255),
                2,
            )
            if args.depth_folder is not None:
                cv2.putText(
                    frame,
                    dist_lines[i],
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (128, 255, 255),
                    2,
                )

        if not_found:
            continue

        cv2.putText(
            frame,
            image.split("/")[-1],
            (130, 130),
            cv2.FONT_HERSHEY_SIMPLEX,
            3.4 * wT / 2000,
            (255, 255, 255),
            3,
        )
        cv2.imshow("YOLO Visualizer", frame)
        key = cv2.waitKey(args.wait)

        if key == ord("q"):
            break
        elif key == ord("o"):
            try:
                os.remove(image)
                print("% s removed successfully" % image)
                image_files = list_files(args.im_folder, IMAGE_EXTENSIONS)
            except OSError as error:
                print(error)
                print("File path can not be removed")
        elif key in range(48, 58):  # sayılar
            with open(txt_path, "w") as f:
                f.write(writeifchangeAll.replace("XXX", str(key - 48)))
        elif key == ord("f"):
            id_image += 1
            id_image = id_image % len(image_files)
        elif key == ord("d"):
            id_image -= 1
            id_image = id_image % len(image_files)
        elif key == ord("c"):
            id_image -= 25
            id_image = id_image % len(image_files)
        elif key == ord("v"):
            id_image += 25
            id_image = id_image % len(image_files)

    except OSError:
        cv2.imshow("YOLO Visualizer", frame)
        key = cv2.waitKey(args.wait)
        if key == ord("q"):
            break

        print("Could not open/read file:", txt_path)
