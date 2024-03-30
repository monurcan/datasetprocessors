
import os
from pathlib import Path

import imagesize

images_path = "/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/WiderPerson_ArabalarVarTemizlenmeliKULLANMA/WiderPerson/images"
labels_path = "/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/WiderPerson_ArabalarVarTemizlenmeliKULLANMA/WiderPerson/Annotations"
outputs_path = "/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/WiderPerson_ArabalarVarTemizlenmeliKULLANMA/WiderPerson/labels"

for file in sorted(Path(labels_path).rglob('*.txt')):
    image_path = os.path.join(images_path, file.stem)
    WIDTH, HEIGHT = imagesize.get(image_path)

    with open(file, "r") as f, open(os.path.join(outputs_path, file.stem.split('.')[0]+".txt"), "w") as f_yolo:
        firstRow = True
        for line in f.readlines():
            if firstRow:
                firstRow = False
                continue

            line_vals = line.split(' ')
            line_vals = [int(line_val) for line_val in line_vals]
            class_id, x_min, y_min, x_max, y_max = line_vals

            x_yolo = (x_min+x_max)/2 / WIDTH
            y_yolo = (y_min+y_max)/2 / HEIGHT
            w_yolo = (x_max-x_min) / WIDTH
            h_yolo = (y_max-y_min) / HEIGHT
            
            f_yolo.write(f"{class_id} {x_yolo} {y_yolo} {w_yolo} {h_yolo}\n")
