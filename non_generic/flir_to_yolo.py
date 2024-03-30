"""
    Run this inside the FLIR folder
"""

from __future__ import print_function

import argparse
import glob
import json
import os
import random

import imagesize

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "image_directory", help='Path of images inside yolo folder that will used for training/testing (will be appended to the begining of imagename in all images names txt)')
    args = parser.parse_args()
    os.mkdir("labels")
    count = 0
    labels = ['person', 'bike', 'car', 'motor', 'bus', 'train',
              'truck', 'light', 'dog', 'scooter', 'other vehicle', 'stroller']
    labels_set = set()

    with open("index.json") as f:
        data = json.load(f)
        frames = data['frames']
        #width, height = 640.0, 512.0
        # width, height = 1800.0, 1600.0
        image_names = []

        for frame in frames:
            image_name = "video-" + frame["videoMetadata"]["videoId"] + "-frame-" + str(
                frame["videoMetadata"]["frameIndex"]).zfill(6) + "-" + frame["datasetFrameId"] + ".jpg"
            image_names.append(args.image_directory + image_name)
            width, height = imagesize.get(args.image_directory + image_name)

            count += 1
            converted_results = []

            for anno in frame["annotations"]:
                label = anno['labels'][0]
                labels_set.add(label)

                if label in labels:
                    bbox_height = anno["boundingBox"]["h"]
                    bbox_width = anno["boundingBox"]["w"]
                    x = anno["boundingBox"]["x"]
                    y = anno["boundingBox"]["y"]
                    cat_id = labels.index(label)

                    x_center, y_center = (
                        x + bbox_width / 2, y + bbox_height / 2)
                    x_rel, y_rel = (x_center / width, y_center / height)
                    w_rel, h_rel = (bbox_width / width, bbox_height / height)
                    converted_results.append(
                        (cat_id, x_rel, y_rel, w_rel, h_rel))

                    c1 = (x, y)
                    c2 = (x+bbox_width, y+bbox_height)

            print(args.image_directory + image_name)
            file = open("labels/" + str(image_name)[:-4] + '.txt', 'w+')
            file.write('\n'.join('%d %.6f %.6f %.6f %.6f' %
                       res for res in converted_results))
            file.close()
        file = open('all_image_names.txt', 'w+')
        file.write('\n'.join('%s' % name for name in image_names))
        file.close()
        print("DONE!!")
        print("Processed", str(count), "images....")

        print(labels_set)
