import os
import sys
from pathlib import Path

import yaml

"""
    This script generates class distribution statistics for a given .yaml file.
    
    Example usage:
        python generate_stats.py /mnt/trains/users/onurcan/Xenics_Onurcan/XenicsOnurcan_15Ekim_withbg_withdrone.yaml
    
    (Then select text to column in excel and select '|' as your delimiter)
"""

if len(sys.argv) < 2:
    print('Please specify the dataset.yaml file')
    sys.exit()

input_file = sys.argv[1]

if not os.path.isfile(input_file):
    print('The dataset.yaml specified does not exist')
    sys.exit()

conf = yaml.safe_load(Path(input_file).read_text())

trainsets = conf['train']
valsets = conf['val']
allsets = trainsets+valsets

labels = conf['names']

print("\t | \t \t | \t \t  # of bounding boxes \t \t")
print("path \t | # of frames \t | ", labels, " total")

for usedset in allsets:
    noframes = len(os.listdir(usedset))
    nobbs = [0] * len(labels)

    labelpath = usedset.replace('images', 'labels')

    if(os.path.isdir(labelpath)):
        for file in os.listdir(labelpath):
            if file.endswith(".txt"):
                for line in open(os.path.join(labelpath, file), "r"):
                    values = line.split(" ")
                    label = int(values[0])

                    if label > len(labels)-1:
                        print("an error occured")
                        print(file)

                    nobbs[label] = nobbs[label] + 1

    print(f"{usedset}|{noframes}|", '|'.join(map(str, nobbs)), '|', sum(nobbs))
