import os
from pathlib import Path
from zipfile import ZipFile

if __name__ == '__main__':
    # dataset_path = "/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/CAMEL"
    # WIDTH, HEIGHT = 336, 256
    # txt_name = "IR"
    # label_paths = [
    #     "Seq1",
    #     "Seq2",
    #     "Seq3",
    #     "Seq4",
    #     "Seq5",
    #     "Seq6",
    #     "Seq7",
    #     "Seq8",
    #     "Seq9",
    #     "Seq10",
    #     "Seq11",
    #     "Seq13",
    #     "Seq15",
    #     "Seq17",
    #     "Seq18",
    #     "Seq19",
    #     "Seq20",
    #     "Seq21",
    #     "Seq23",
    #     "Seq25",
    #     "Seq26",
    #     "Seq27",
    #     "Seq28",
    #     "Seq29",
    #     "Seq30",
    # ]

    dataset_path = "/mnt/RawInternalDatasets/KaraGAG/MWIR/FromWeb/CAMEL"
    WIDTH, HEIGHT = 336, 256
    txt_name = "IR"
    label_paths = [
        "Seq1",
        "Seq2",
        "Seq3",
        "Seq4",
        "Seq5",
        "Seq6",
        "Seq7",
        "Seq8",
        "Seq9",
        "Seq10",
        "Seq11",
        "Seq13",
        "Seq15",
        "Seq17",
        "Seq18",
        "Seq19",
        "Seq20",
        "Seq21",
        "Seq23",
        "Seq25",
        "Seq26",
        "Seq27",
        "Seq28",
        "Seq30",
    ]

    # for path in sorted(Path(dataset_path).rglob('*.zip')):
    #     dir_name = "/".join(str(path).split('/')[:-1])+"/"+"images"
    #     print(dir_name)
    #     os.makedirs(dir_name)
    #     zf = ZipFile(path, 'r')
    #     zf.extractall(dir_name)
    #     zf.close()

    label_paths = [os.path.join(dataset_path, label_path)
                   for label_path in label_paths]

    labels = set()

    for label_path in label_paths:
        output_path = os.path.join(label_path, "labels")
        os.makedirs(output_path, exist_ok=True)

        label_path = os.path.join(
            label_path, label_path.split("/")[-1]+"-"+txt_name+".txt")
        print(label_path)

        with open(label_path) as f:
            for line in f.readlines():
                if not line.strip():
                    continue

                frame_number, track_id, label, x_min, y_min, bb_width, bb_height = line.split()
                x_min, y_min, bb_width, bb_height = float(x_min), float(
                    y_min), float(bb_width), float(bb_height)

                x_yolo = (x_min + bb_width/2) / WIDTH
                y_yolo = (y_min + bb_height/2) / HEIGHT
                w_yolo = bb_width / WIDTH
                h_yolo = bb_height / HEIGHT

                if label in ['2', '3']:
                    yolo_label = 0
                elif label in ['1']:
                    yolo_label = 1
                elif label in ['18']:
                    yolo_label = 2
                else:
                    print("ERROR!!!!")

                with open(os.path.join(output_path, str(frame_number).zfill(6)+".txt"), "a") as f_yolo:
                    f_yolo.write(
                        f"{yolo_label} {x_yolo} {y_yolo} {w_yolo} {h_yolo}\n")

                labels.add(label)

    print(labels)
