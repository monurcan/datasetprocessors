import math
import os

output_path = "/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/UAV123/UAV123/yolo/labels"
image_path = "/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/UAV123/UAV123/yolo/images"
label_path = "/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/UAV123/UAV123/anno/UAV123"
label_folders = ["person1",
                 "person1_s",
                 "person2",
                 "person2_s",
                 "person3",
                 "person3_s",
                 "person4",
                 "person5",
                 "person6",
                 "person7",
                 "person8",
                 "person9",
                 "person10",
                 "person11",
                 "person12",
                 "person13",
                 "person14",
                 "person15",
                 "person16",
                 "person17",
                 "person18",
                 "person19",
                 "person20",
                 "person21",
                 "person22",
                 "person23"]

WIDTH, HEIGHT = 1280, 720

for label_folder in label_folders:
    print(label_folder)

    with open(os.path.join(label_path, label_folder)+".txt", "r") as f:
        for i, line in enumerate(f.readlines()):
            file_name = str(i+1).zfill(6)+".txt"
            x_tl, y_tl, w, h = [float(val) for val in line.split(',')]
            x_yolo, y_yolo = x_tl+w/2, y_tl+h/2

            if math.isnan(x_yolo) or math.isnan(y_yolo) or math.isnan(w) or math.isnan(h):
                img_path = os.path.join(
                    image_path, label_folder, file_name.replace(".txt", ".jpg"))
                if os.path.exists(img_path):
                    os.remove(img_path)

            with open(os.path.join(output_path, label_folder, file_name), "w") as f_yolo:
                f_yolo.write(
                    f"1 {x_yolo/WIDTH} {y_yolo/HEIGHT} {w/WIDTH} {h/HEIGHT}")
