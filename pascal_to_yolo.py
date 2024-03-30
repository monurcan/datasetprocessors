import argparse
import glob
import json
import logging
import os
import xml.etree.ElementTree as ET


def xml_to_yolo_bbox(bbox, w, h):
    # xmin, ymin, xmax, ymax
    x_center = ((bbox[2] + bbox[0]) / 2) / w
    y_center = ((bbox[3] + bbox[1]) / 2) / h
    width = (bbox[2] - bbox[0]) / w
    height = (bbox[3] - bbox[1]) / h
    return [x_center, y_center, width, height]


def yolo_to_xml_bbox(bbox, w, h):
    # x_center, y_center width heigth
    w_half_len = (bbox[2] * w) / 2
    h_half_len = (bbox[3] * h) / 2
    xmin = int((bbox[0] * w) - w_half_len)
    ymin = int((bbox[1] * h) - h_half_len)
    xmax = int((bbox[0] * w) + w_half_len)
    ymax = int((bbox[1] * h) + h_half_len)
    return [xmin, ymin, xmax, ymax]


def pascal_to_yolo(classes, files, output_dir):
    # loop through each xml
    for fil in files:
        basename = os.path.basename(fil)
        filename = os.path.splitext(basename)[0]

        result = []

        # parse the content of the xml file
        tree = ET.parse(fil)
        root = tree.getroot()
        width = int(root.find("size").find("width").text)
        height = int(root.find("size").find("height").text)

        for obj in root.findall('object'):
            label = obj.find("name").text
            # check for new classes and append to list
            if label not in classes:
                logging.warning(
                    f"{label} is not specified in label order argument!")
            else:
                index = classes[label]
                pil_bbox = [float(x.text) for x in obj.find("bndbox")]
                yolo_bbox = xml_to_yolo_bbox(pil_bbox, width, height)
                # convert data to string
                bbox_string = " ".join([str(x) for x in yolo_bbox])
                result.append(f"{index} {bbox_string}")

        if result:
            # generate a YOLO format text file for each xml file
            with open(os.path.join(output_dir, f"{filename}.txt"), "w", encoding="utf-8") as f:
                f.write("\n".join(result))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='CVAT to YOLO format converter.')
    parser.add_argument('--input_dir', required=True, type=str,
                        help="Annotations path")
    parser.add_argument('--output_dir', required=True, type=str,
                        help="Output path")
    parser.add_argument('--labels_order', default="Vehicle=0, Person=1, Animal=2, Herd=3, Antitank=4", type=str,
                        help="Specify the label order for integer class ID mapping, example: 'Vehicle=0, Person=1, Animal=2, Herd=3, Antitank=4', if an empty argument '' is provided, the order in the xml file is used")
    args = parser.parse_args()

    classes_dict = dict([label.strip().split("=")
                   for label in args.labels_order.split(',')])

    # create the labels folder (output directory)
    os.makedirs(args.output_dir, exist_ok=True)

    # identify all the xml files in the annotations folder (input directory)
    all_files = glob.glob(os.path.join(args.input_dir, '*.xml'))

    pascal_to_yolo(classes_dict, all_files, args.output_dir)
