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

color_mapper = {
  0: (0, 0, 255), # vehicle
  1: (0, 255, 0), # person
  2: (255, 0, 0), # animal
  3:(255, 255, 102), #herd
  4: (169, 39, 117), # antitank
}

def list_files(path, ext):
    files_ = []
    for root, _, files in os.walk(path):
        for f in files:
            if f.lower().endswith(ext):
                files_.append(os.path.join(root, f))

    return natsorted(files_)


parser = argparse.ArgumentParser(description='Test YOLO data.')
parser.add_argument('--im_folder', required=True)
parser.add_argument('--txt_folder')
parser.add_argument(
    '--labels', default="vehicle,person,animal,herd,antitank,drone")
parser.add_argument('--wait', type=int, default=0)
parser.add_argument('--find', type=int)
args = parser.parse_args()

IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')
image_files = list_files(args.im_folder, IMAGE_EXTENSIONS)

label_names = args.labels.split(',')

if args.txt_folder is None:
    args.txt_folder = args.im_folder.replace('images', 'labels')

#cv2.namedWindow("YOLO Visualizer", cv2.WINDOW_NORMAL)

skip_counter = 0
not_found = False

for idx, image in enumerate(tqdm(image_files)):
    if skip_counter > 0:
        skip_counter -= 1
        time.sleep(0.015)
        continue

    if(args.find is None):
        frame = cv2.imread(image)

    coordinates = []

    txt_path = os.path.splitext(image)[0]

    if args.txt_folder is not None:
        txt_path = os.path.join(args.txt_folder, txt_path.split('/')[-1])

    txt_path += ".txt"

    try:
        lines = open(txt_path, "r")
        writeifchangeAll = ""

        with lines:
            for line in lines:
                coordinates = line.rstrip('\n').split(' ')
                idx = coordinates[0]

                if(args.find is not None):
                    if(idx != str(args.find)):
                        not_found = True
                        continue
                    else:
                        frame = cv2.imread(image)
                        not_found = False

                hT, wT, cT = frame.shape
                x1, y1, w2, h2 = float(coordinates[1]), float(
                    coordinates[2]), float(coordinates[3]), float(coordinates[4])
                # print(x1,y1,w2,h2)
                w, h = int(w2 * wT), int(h2 * hT)
                x, y = int((x1 * wT) - w / 2), int((y1 * hT) - h / 2)

                writeifchangeAll += f"XXX {x1} {y1} {w2} {h2}\n"

                cv2.rectangle(frame, (x, y), (x+w, y+h), color_mapper[int(idx)], 2)
                # cv2.putText(frame, label_names[int(
                #     idx)], (x, y+10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (128, 0, 255), 2)
        if not_found:
            continue

        # cv2.putText(frame, image.split(
        #     '/')[-1], (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 0)
        #cv2.imshow("YOLO Visualizer", frame)
        #print("/mnt/onurcan/visualize12haziran/inference0/"+image.split('/')[-1])
        cv2.imwrite("/mnt/onurcan/visualize12haziran/inference2/"+image.split('/')[-1], frame)
        #key = cv2.waitKey(args.wait)

        # if key == ord('q'):
        #     break
        # elif key == ord('v'):
        #     skip_counter = 25
        # elif key == ord('o'):
        #     try:
        #         os.remove(image)
        #         print("% s removed successfully" % image)
        #     except OSError as error:
        #         print(error)
        #         print("File path can not be removed")
        # elif key in range(48, 58):  # sayılar
        #     with open(txt_path, "w") as f:
        #         f.write(writeifchangeAll.replace("XXX", str(key-48)))

    except OSError:
        # cv2.imshow("YOLO Visualizer", frame)
        # key = cv2.waitKey(args.wait)
        # if key == ord('q'):
        #     break
        
        frame = cv2.imread(image)
        cv2.imwrite("/mnt/onurcan/visualize12haziran/inference2/"+image.split('/')[-1], frame)
        

        print("Could not open/read file:", txt_path)
