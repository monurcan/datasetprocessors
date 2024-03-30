import os

if __name__ == '__main__':
    label_paths = [
        "/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/VerschoorAerialCow/conservationDronesECCVwData/dataset/annotations/COW809_1.txt",
        "/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/VerschoorAerialCow/conservationDronesECCVwData/dataset/annotations/COW809_2.txt",
        "/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/VerschoorAerialCow/conservationDronesECCVwData/dataset/annotations/COW809_3.txt",
        "/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/VerschoorAerialCow/conservationDronesECCVwData/dataset/annotations/COW809_4.txt",
        "/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/VerschoorAerialCow/conservationDronesECCVwData/dataset/annotations/COW810_1.txt",
        "/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/VerschoorAerialCow/conservationDronesECCVwData/dataset/annotations/COW810_2.txt"
    ]
    output_paths = [
        "/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/VerschoorAerialCow/conservationDronesECCVwData/dataset/labels/GOPR0809_start_0_27_end_1_55",
        "/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/VerschoorAerialCow/conservationDronesECCVwData/dataset/labels/GOPR0809_start_2_09_end_2_27",
        "/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/VerschoorAerialCow/conservationDronesECCVwData/dataset/labels/GOPR0809_start_2_40_end_3_20",
        "/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/VerschoorAerialCow/conservationDronesECCVwData/dataset/labels/GOPR0809_start_5_05_end_6_11",
        "/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/VerschoorAerialCow/conservationDronesECCVwData/dataset/labels/GOPR0810_start_1_10_end_1_55",
        "/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/VerschoorAerialCow/conservationDronesECCVwData/dataset/labels/GOPR0810_start_2_30_end_3_20"
    ]
    WIDTH, HEIGHT = 1920, 1080

    for label_path, output_path in zip(label_paths, output_paths):

        os.makedirs(output_path, exist_ok=True)

        labels = set()

        with open(label_path) as f:
            for line in f.readlines():
                track_id, x_min, y_min, x_max, y_max, frame, lost, occluded, generated, label = line.split(
                    " ")

                track_id, x_min, y_min, x_max, y_max, lost, occluded, generated = int(track_id), int(
                    x_min), int(y_min), int(x_max), int(y_max), int(lost), int(occluded), int(generated)

                if(occluded == 1 or lost == 1):
                    continue

                x_yolo = (x_min+x_max)/2 / WIDTH
                y_yolo = (y_min+y_max)/2 / HEIGHT
                w_yolo = (x_max-x_min) / WIDTH
                h_yolo = (y_max-y_min) / HEIGHT

                # print(track_id, x_min, y_min, x_max, y_max,
                #   frame, lost, occluded, generated, label)

                with open(os.path.join(output_path, "frame_"+str(frame).zfill(6)+".txt"), "a") as f_yolo:
                    f_yolo.write(f"2 {x_yolo} {y_yolo} {w_yolo} {h_yolo}\n")

                labels.add(label)

        # print(labels)
