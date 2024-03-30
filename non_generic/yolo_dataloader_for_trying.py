
import contextlib
import glob
import hashlib
import json
import math
import os
import random
import shutil
import time
from itertools import repeat
from multiprocessing.pool import Pool, ThreadPool
from pathlib import Path
from threading import Thread
from urllib.parse import urlparse

import numpy as np
import psutil
import torch
import torch.nn.functional as F
import torchvision
import yaml
from PIL import ExifTags, Image, ImageOps
from torch.utils.data import DataLoader, Dataset, dataloader, distributed
from tqdm import tqdm

# include image suffixes
IMG_FORMATS = 'bmp', 'dng', 'jpeg', 'jpg', 'mpo', 'png', 'tif', 'tiff', 'webp', 'pfm'

f = []
# os-agnostic
p = Path("/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/TinyPerson/images")
if p.is_dir():  # dir
    f += glob.glob(str(p / '**' / '*.*'), recursive=True)
    # f = list(p.rglob('*.*'))  # pathlib
elif p.is_file():  # file
    with open(p) as t:
        t = t.read().strip().splitlines()
        parent = str(p.parent) + os.sep
        f += [x.replace('./', parent, 1) if x.startswith('./')
              else x for x in t]  # to global path
        # f += [p.parent / x.lstrip(os.sep) for x in t]  # to global path (pathlib)
else:
    raise FileNotFoundError(f'{p} does not exist')
im_files = sorted(x.replace('/', os.sep)
                  for x in f if x.split('.')[-1].lower() in IMG_FORMATS)
print(im_files)
