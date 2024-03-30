import glob
import os
import sys
from pathlib import Path
import shutil

import yaml

if len(sys.argv) < 2:
    print('Please specify the dataset.yaml file')
    sys.exit()

input_file = sys.argv[1]
new_path = sys.argv[2]

if not os.path.isfile(input_file):
    print('The dataset.yaml specified does not exist')
    sys.exit()
    
# create images and labels folders in new_path
if not os.path.exists(new_path):
    os.makedirs(new_path)
    os.makedirs(os.path.join(new_path, "images"))
    os.makedirs(os.path.join(new_path, "labels"))

conf = yaml.safe_load(Path(input_file).read_text())

trainsets = conf['train']
valsets = conf['val']
dataset_root = conf['path']
allsets = [os.path.join(dataset_root, x) for x in trainsets+valsets]

labels = conf['names']

# print("\t | \t \t | \t \t  # of bounding boxes \t \t")
# print("path \t | # of frames \t | ", labels, " total")

IMG_FORMATS = 'bmp', 'dng', 'jpeg', 'jpg', 'mpo', 'png', 'tif', 'tiff', 'webp', 'pfm'


def img2label_paths(img_paths):
    # Define label paths as a function of image paths
    # /images/, /labels/ substrings
    sa, sb = f'{os.sep}images{os.sep}', f'{os.sep}labels{os.sep}'
    return [sb.join(x.rsplit(sa, 1)).rsplit('.', 1)[0] + '.txt' for x in img_paths]

total_num_copies = 0

for usedset in allsets:
    nobbs = [0] * len(labels)

    if os.path.isdir(usedset):
        f = glob.glob(str(Path(usedset) / '**' / '*.*'), recursive=True)
        im_files = sorted(x.replace('/', os.sep)
                          for x in f if x.split('.')[-1].lower() in IMG_FORMATS)  # not sorted
        label_files = img2label_paths(im_files)
        noframes = len(im_files)

        for im_file, file in zip(im_files, label_files):
            if os.path.exists(file):
                for line in open(file, "r"):
                    if line.strip():
                        values = line.split(" ")
                        label = int(values[0])

                        if label > len(labels)-1:
                            print("an error occured: ", file)
                            
                        # if label == 4: # antitank
                        if label == 4 or (label == 2 or label == 3): # animal herd
                            # print(file)
                            # print(im_file)
                            
                            """
                                TODO: copy with a new name indicating the original folder
                                otherwise collision occurs
                            """
                            # copy files to new_path
                            shutil.copy(im_file, os.path.join(new_path, "images"))
                            shutil.copy(file, os.path.join(new_path, "labels"))
                            
                            total_num_copies += 1
                            
                            break

                        nobbs[label] = nobbs[label] + 1
    else:
        print("not a directory", usedset)

    # print(f"{usedset}|{noframes}|", '|'.join(map(str, nobbs)), '|', sum(nobbs))

print(total_num_copies)