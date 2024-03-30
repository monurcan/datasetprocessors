import os
from pathlib import Path

import imagesize

folder = "/mnt/RawInternalDatasets/USV/110523_dearsan/thermal/cvat_11_05_2023_14_12_43_0"

img_files = list(Path(folder).rglob('*'))

for file in img_files:
    if not os.path.isfile(file):
        continue

    if os.path.getsize(file) < 10:
        print(file)

    width, height = imagesize.get(file)
    if width != 640 or height != 512:
        print(width, height)
        print(file)
