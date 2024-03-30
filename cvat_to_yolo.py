import argparse
import json
import math
import os
import pathlib
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import pandas as pd
from lxml import etree
from natsort import natsorted
from wcmatch.pathlib import Path

"""
    This script directly converts CVAT format to YOLO format.

    input folder structure
        | images/ (not necessarily for CVAT for images)
        | cvat_annotations.zip
    
    Example usage:
        python cvat_to_yolo.py --folder /mnt/RawInternalDatasets/karagag/Fujinon/VK/243 --filters "attribute_Is texture visible?=Yes, occluded=0"
        
    Note: In VK, CVAT for images does not output "outside" information, but, CVAT for videos does. Therefore use CVAT for videos.
"""


def find_zip_file(folder):
    zip_files = list(pathlib.Path(folder).glob('*.zip'))

    if len(zip_files) != 1:
        raise NameError(
            'There should be one cvat_annotations.zip file in the input folder!')

    return zip_files[0]


def label_order_parser(labels_order, annotations_path):
    if labels_order.strip():
        return dict([label.strip().split("=") for label in labels_order.split(',')])
    else:
        with open(annotations_path, "rb") as xml_file:
            xml = xml_file.read()

        root = etree.fromstring(xml)

        return dict((v, str(k)) for k, v in dict(enumerate(root.xpath("//meta/task/labels/label/name/text()"))).items())


def cvat_bb_to_yolo_bb(x1, y1, x2, y2, image_w, image_h):
    x1, y1, x2, y2, image_w, image_h = float(x1), float(
        y1), float(x2), float(y2), float(image_w), float(image_h)

    return [((x2 + x1)/(2*image_w)), ((y2 + y1)/(2*image_h)), (x2 - x1)/image_w, (y2 - y1)/image_h]


def cvat_to_yolo(fname, txt_path, filtered_fields, label_order_mapper, img_ordering):
    """
    Convert CVAT annotation from xml to YOLO format:
    https://github.com/opencv/cvat/blob/develop/cvat/apps/documentation/xml_format.md
    :param fname: xml file name
    :param txt_path: txt files path
    """

    def _parse_points(value):
        """
        Helper function for transform CVAT points from format `x1,y2;x2,y2;..;xn,yn`
         to format [[x1, x2], [x2, y2], ..., [xn, yn]]
        :param value: string of points. If no string is given, return the same value
        :return: points
        """
        if isinstance(value, str):
            return [[float(point) for point in points.split(",")]
                    for points in value.split(";")]
        return value

    with open(fname, "rb") as xml_file:
        xml = xml_file.read()

    root = etree.fromstring(xml)

    image_width, image_height = root.xpath("//meta/task/original_size/width/text()")[
        0], root.xpath("//meta/task/original_size/height/text()")[0]

    for item in root.getchildren():
        if item.tag != "track" and item.tag != "image":
            continue

        img_properties = dict(item.attrib)
        img_properties_width = image_width if item.tag == "track" else img_properties[
            'width']
        img_properties_height = image_height if item.tag == "track" else img_properties[
            'height']

        if item.tag == "image":
            txt_file = open(os.path.join(
                txt_path, img_properties['name']+".txt"), 'w')
            dict_label = ''
        else:
            txt_file = ''
            dict_label = img_properties['label']

        for record in item.getchildren():
            writePerBox(record, filtered_fields, label_order_mapper,
                        img_properties_width, img_properties_height, txt_file, txt_path, img_ordering, dict_label)

        if item.tag == "image":
            txt_file.close()


def writePerBox(record, filtered_fields, label_order_mapper, img_properties_width, img_properties_height, txt_file, txt_path, img_ordering, dict_label):
    dict_ = dict(record.attrib)

    dict_["type"] = record.tag
    for attribute in record:
        dict_[f"attribute_{attribute.attrib['name']}"] = attribute.text

    if dict_label == '':
        dict_label = dict_['label']

    class_id = label_order_mapper[dict_label]

    yolo_bb = cvat_bb_to_yolo_bb(dict_['xtl'], dict_['ytl'], dict_['xbr'], dict_[
        'ybr'], img_properties_width, img_properties_height)
    yolo_bb = [str(coord) for coord in yolo_bb]
    yolo_bb = [class_id] + yolo_bb

    # Filtering
    compare_filters = list(
        dict_.get(k, v) != v for k, v in filtered_fields.items())

    if any(compare_filters):
        # print(img_properties['name'])
        # print(dict_)
        return
    else:
        if(txt_file != ''):
            txt_file.write(' '.join(yolo_bb) + '\n')
        else:
            with open(os.path.join(txt_path, img_ordering[int(dict_['frame'])]+".txt"), 'a') as f_yolo:
                f_yolo.write(' '.join(yolo_bb) + '\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='CVAT to YOLO format converter.')
    parser.add_argument('--folder', default="", type=str,
                        help="Where the data is stored (the input folder should include images folder (not necessarily for CVAT for images) and cvat_annotations.zip file)")
    parser.add_argument('--filters', default="occluded=0, outside=0", type=str,
                        help="Specify in the form of 'field name = value', only the annotations satisfying all the conditions will be written, example: 'attribute_Name 1=No, attribute_Is texture visible?=Yes, attribute_Is Dynamic?=No, occluded=0'")
    parser.add_argument('--labels_order', default="Vehicle=0, Person=1, Animal=2, Herd=3, Antitank=4, Half_Body=1, Other=2", type=str,
                        help="Specify the label order for integer class ID mapping, example: 'Vehicle=0, Person=1, Animal=2, Herd=3, Antitank=4', if an empty argument '' is provided, the order in the xml file is used")
    args = parser.parse_args()

    print(f"Processing started for {args.folder}")

    # Find CVAT annotations.zip file
    cvat_annotations_zip = find_zip_file(args.folder)

    # Extract the CVAT annotations.zip file
    with zipfile.ZipFile(cvat_annotations_zip) as zip_ref:
        zip_ref.extractall(args.folder)
    annotations_path = os.path.join(args.folder, "annotations.xml")

    # Create labels directory
    labels_path = os.path.join(args.folder, "labels")
    os.makedirs(labels_path, exist_ok=True)

    # Parse the filters argument
    filtered_fields = dict([filter.strip().split("=")
                            for filter in args.filters.split(',')]) if args.filters.strip() else {}

    # Labels to integer class ID mapping
    label_order_mapper = label_order_parser(
        args.labels_order, annotations_path)

    # Get the order of the images in the /images folder
    img_ordering = ["frame_"+str(number).zfill(6) for number in range(20000)]
    # img_ordering = natsorted([path.stem for path in Path(os.path.join(args.folder, 'images')).glob(
    #     ['*.png', '*.PNG', '*.jpg', '*.JPG', '*.jpeg', '*.JPEG', '*.bmp', '*.BMP'])])

    # Create YOLO .txt files
    cvat_to_yolo(annotations_path, labels_path,
                 filtered_fields, label_order_mapper, img_ordering)
