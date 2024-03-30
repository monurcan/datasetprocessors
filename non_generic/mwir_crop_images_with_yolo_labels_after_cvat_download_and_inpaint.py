import argparse
import os
from pathlib import Path

import cv2
from tqdm import tqdm

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Image cropper with YOLO labels.")

    parser.add_argument(
        "--folder", required=True, type=str, help="Where the images are stored"
    )
    parser.add_argument("--img_ext", default="PNG", type=str, help="Image extension")
    parser.add_argument(
        "--mask_path",
        type=str,
        help="Mask path",
        default="inpaint_masks/mwir_new.jpg",
    )
    args = parser.parse_args()

    if args.folder[-1] == "/":
        args.folder = args.folder[:-1]

    dest_folder = args.folder + "_cropped"
    os.makedirs(dest_folder, exist_ok=True)
    label_dest_folder = args.folder.replace("/images", "/labels") + "_cropped"
    os.makedirs(label_dest_folder, exist_ok=True)

    mask = cv2.imread(args.mask_path, 0)
    _, mask = cv2.threshold(mask, 128, 255, cv2.THRESH_BINARY_INV)

    for path in tqdm(sorted(Path(args.folder).rglob("*." + args.img_ext))):
        img = cv2.imread(str(path))
        image_height, image_width, _ = img.shape

        # change this for different crop settings
        crop_tl_x = 72
        crop_tl_y = 57
        crop_br_x = 1207
        crop_br_y = 965

        cropped_ = img[crop_tl_y:crop_br_y, crop_tl_x:crop_br_x]
        cropped = cv2.inpaint(cropped_, mask, 3, cv2.INPAINT_TELEA)
        cv2.imwrite(os.path.join(dest_folder, path.name), cropped)
        # yolo will resize, not required here
        new_image_width, new_image_height = crop_br_x - crop_tl_x, crop_br_y - crop_tl_y

        with open(
            str(path)
            .replace("/images", "/labels_cropped")
            .replace("." + args.img_ext, ".txt"),
            "w",
        ) as f_cropped, open(
            str(path).replace("/images", "/labels").replace("." + args.img_ext, ".txt"),
            "r",
        ) as f_original:
            for line in f_original.readlines():
                label, bb_x, bb_y, bb_w, bb_h = line.split()
                bb_x, bb_y, bb_w, bb_h = (
                    float(bb_x),
                    float(bb_y),
                    float(bb_w),
                    float(bb_h),
                )
                tl_x, tl_y, br_x, br_y = (
                    (bb_x - bb_w / 2) * image_width,
                    (bb_y - bb_h / 2) * image_height,
                    (bb_x + bb_w / 2) * image_width,
                    (bb_y + bb_h / 2) * image_height,
                )

                tl_x -= crop_tl_x
                tl_y -= crop_tl_y
                br_x -= crop_tl_x
                br_y -= crop_tl_y

                tl_x = max(tl_x, 0)
                tl_y = max(tl_y, 0)
                br_x = min(br_x, new_image_width)
                br_y = min(br_y, new_image_height)

                # size filter
                # w_threshold = 7.0  # px
                # h_threshold = 7.0  # px
                # area_threshold = 100.0  # px2
                # if (
                #     (br_x - tl_x) < w_threshold
                #     or (br_y - tl_y) < h_threshold
                #     or (br_x - tl_x) * (br_y - tl_y) < area_threshold
                # ):
                #     continue

                new_yolo_x, new_yolo_y, new_yolo_w, new_yolo_h = (
                    (tl_x + br_x) / 2 / new_image_width,
                    (tl_y + br_y) / 2 / new_image_height,
                    (br_x - tl_x) / new_image_width,
                    (br_y - tl_y) / new_image_height,
                )

                f_cropped.write(
                    f"{label} {new_yolo_x} {new_yolo_y} {new_yolo_w} {new_yolo_h}\n"
                )
