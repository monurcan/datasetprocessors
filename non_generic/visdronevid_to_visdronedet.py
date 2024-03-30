import os

# video_names = [
#     "uav0000009_03358_v",
#     "uav0000073_00600_v",
#     "uav0000073_04464_v",
#     "uav0000077_00720_v",
#     "uav0000088_00290_v",
#     "uav0000119_02301_v",
#     "uav0000120_04775_v",
#     "uav0000161_00000_v",
#     "uav0000188_00000_v",
#     "uav0000201_00000_v",
#     "uav0000249_00001_v",
#     "uav0000249_02688_v",
#     "uav0000297_00000_v",
#     "uav0000297_02761_v",
#     "uav0000306_00230_v",
#     "uav0000355_00001_v",
#     "uav0000370_00001_v"
# ]
# annotations_vid_path = "/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/VisDrone/VisDrone2019-VID-test-dev/annotations_vid"
# outputs_path = "/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/VisDrone/VisDrone2019-VID-test-dev/annotations"

# video_names = [
#     "uav0000013_00000_v",
#     "uav0000013_01073_v",
#     "uav0000013_01392_v",
#     "uav0000020_00406_v",
#     "uav0000071_03240_v",
#     "uav0000072_04488_v",
#     "uav0000072_05448_v",
#     "uav0000072_06432_v",
#     "uav0000076_00720_v",
#     "uav0000079_00480_v",
#     "uav0000084_00000_v",
#     "uav0000099_02109_v",
#     "uav0000124_00944_v",
#     "uav0000126_00001_v",
#     "uav0000138_00000_v",
#     "uav0000140_01590_v",
#     "uav0000143_02250_v",
#     "uav0000145_00000_v",
#     "uav0000150_02310_v",
#     "uav0000218_00001_v",
#     "uav0000222_03150_v",
#     "uav0000239_03720_v",
#     "uav0000239_12336_v",
#     "uav0000243_00001_v",
#     "uav0000244_01440_v",
#     "uav0000248_00001_v",
#     "uav0000263_03289_v",
#     "uav0000264_02760_v",
#     "uav0000266_03598_v",
#     "uav0000266_04830_v",
#     "uav0000270_00001_v",
#     "uav0000273_00001_v",
#     "uav0000278_00001_v",
#     "uav0000279_00001_v",
#     "uav0000281_00460_v",
#     "uav0000288_00001_v",
#     "uav0000289_00001_v",
#     "uav0000289_06922_v",
#     "uav0000295_02300_v",
#     "uav0000300_00000_v",
#     "uav0000307_00000_v",
#     "uav0000308_00000_v",
#     "uav0000308_01380_v",
#     "uav0000309_00000_v",
#     "uav0000315_00000_v",
#     "uav0000316_01288_v",
#     "uav0000323_01173_v",
#     "uav0000326_01035_v",
#     "uav0000329_04715_v",
#     "uav0000342_04692_v",
#     "uav0000352_05980_v",
#     "uav0000357_00920_v",
#     "uav0000360_00001_v",
#     "uav0000361_02323_v",
#     "uav0000363_00001_v",
#     "uav0000366_00001_v",
# ]
# annotations_vid_path = "/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/VisDrone/VisDrone2019-VID-train/annotations_vid"
# outputs_path = "/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/VisDrone/VisDrone2019-VID-train/annotations"

video_names = [
    "uav0000086_00000_v",
    "uav0000117_02622_v",
    "uav0000137_00458_v",
    "uav0000182_00000_v",
    "uav0000268_05773_v",
    "uav0000305_00000_v",
    "uav0000339_00001_v",
]
annotations_vid_path = "/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/VisDrone/VisDrone2019-VID-val/annotations_vid"
outputs_path = "/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/VisDrone/VisDrone2019-VID-val/annotations"


for video_name in video_names:
    annotation_vid_path = os.path.join(annotations_vid_path, video_name+".txt")
    os.makedirs(os.path.join(outputs_path, video_name), exist_ok=True)
    print(annotation_vid_path)

    with open(annotation_vid_path, "r") as f_vid:
        for line in f_vid.readlines():
            line_elements = line.split(",")
            frame_id = line_elements[0]
            line_elements = line_elements[2:]

            output_path = os.path.join(
                outputs_path, video_name, frame_id.zfill(7)+".txt")

            # print(output_path)

            with open(output_path, "a") as f_det:
                f_det.write(",".join(line_elements))
