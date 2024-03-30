import argparse
import json
import os
from pathlib import Path

from natsort import natsorted

"""
    This script directly converts CVAT backup format to YOLO format.
    
    Example usage:
        python cvat_backup_to_yolo.py -j annotations.json -o path_to_dir
"""

parser = argparse.ArgumentParser(description='COCO to YOLO format converter.')
parser.add_argument('-j', help='JSON file', dest='json', required=True)
parser.add_argument('-o', help='Path to output folder',
                    dest='out', required=True)
parser.add_argument('-i', help='Path to img folder',
                    required=True)
parser.add_argument('-id2name', default="99=suustunesne,100=buyukgemi,101=kucukbottekne,102=yelkenli,103=ida_albatros_s,104=diger_businiflarauymayansiniflandirilamayan,105=ida_albatros_t", type=str, help="Specify the ID")
parser.add_argument('-labels_order', default="suustunesne=0, buyukgemi=1, kucukbottekne=2, yelkenli=3, ida_albatros_s=4, diger_businiflarauymayansiniflandirilamayan=5, ida_albatros_t=6", type=str,
                    help="Specify the label order for integer class ID mapping, example: 'Vehicle=0, Person=1, Animal=2, Herd=3, Antitank=4', if an empty argument '' is provided, the order in the xml file is used")
parser.add_argument('-image_width', default=2880, type=int)
parser.add_argument('-image_height', default=1860, type=int)
args = parser.parse_args()

if __name__ == '__main__':
    id2name = dict([label.strip().split('=') for label in args.id2name.split(',')])
    id2name = {int(k):v for k,v in id2name.items()}
    
    label_order_mapper = dict([label.strip().split("=")
                               for label in args.labels_order.split(',')])

    json_file = args.json
    output = args.out

    os.makedirs(output)

    img_list = natsorted(list(Path(args.i).glob("*.png")))
    with open(json_file) as f:
        # data = json.load(f)[0]
        data = json.load(f)

        all_shapes = data['shapes']
        for track in data['tracks']:
            if not track['shapes']:
                continue

            last_frame_id = track['shapes'][0]['frame'] - 1

            track_shapes = []

            for shape in track['shapes']:
                shape['label'] = id2name[track['label_id']]
                if shape['outside'] or shape['occluded']:
                    last_frame_id = -1
                    last_xtl, last_ytl, last_xbr, last_ybr = shape['points']

                    continue

                track_shapes.append(shape)

                if last_frame_id + 1 != shape['frame'] and last_frame_id != -1:
                    cur_xtl, cur_ytl, cur_xbr, cur_ybr = shape['points']
                    slope_xtl, slope_ytl, slope_xbr, slope_ybr = \
                        (cur_xtl-last_xtl)/(shape['frame']-last_frame_id), \
                        (cur_ytl-last_ytl)/(shape['frame']-last_frame_id), \
                        (cur_xbr-last_xbr)/(shape['frame']-last_frame_id), \
                        (cur_ybr-last_ybr)/(shape['frame']-last_frame_id)

                    for index in range(1, shape['frame'] - last_frame_id):
                        interpolated_id = index + last_frame_id

                        interpolated_shape = shape.copy()
                        interpolated_shape['frame'] = interpolated_id
                        interpolated_shape['points'] = [
                            last_xtl + index * slope_xtl,
                            last_ytl + index * slope_ytl,
                            last_xbr + index * slope_xbr,
                            last_ybr + index * slope_ybr
                        ]
                        track_shapes.append(interpolated_shape)

                last_frame_id = shape['frame']
                last_xtl, last_ytl, last_xbr, last_ybr = shape['points']

            all_shapes.extend(track_shapes)

        for shape in all_shapes:
            with open(os.path.join(output, str(img_list[shape['frame']].stem)+".txt"), "a") as f_yolo:
                x_yolo = (shape['points'][2]+shape['points'][0]) / \
                    2 / args.image_width
                w_yolo = (shape['points'][2]-shape['points']
                          [0]) / args.image_width
                y_yolo = (shape['points'][3]+shape['points'][1]) / \
                    2 / args.image_height
                h_yolo = (shape['points'][3]-shape['points']
                          [1]) / args.image_height

                if 'label' in shape:
                    class_name = shape['label']
                elif 'label_id' in shape:
                    class_name = id2name[shape['label_id']]
                else:
                    print(shape)
                    raise NameError("label or label_id does not exist in shape.")
                f_yolo.write(
                    f"{label_order_mapper[class_name]} {x_yolo} {y_yolo} {w_yolo} {h_yolo}\n")
