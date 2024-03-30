import argparse
import os
import shutil


def move_txt_files(input_folder):
    for root, dirs, files in os.walk(input_folder):
        if "obj_train_data" in dirs:
            obj_train_data_path = os.path.join(root, "obj_train_data")
            labels_path = os.path.join(root, "labels")
            os.makedirs(labels_path, exist_ok=True)

            # Move .txt files to the 'labels' folder
            for file in os.listdir(obj_train_data_path):
                if file.endswith(".txt"):
                    shutil.move(os.path.join(obj_train_data_path, file), labels_path)

            # Rename 'obj_train_data' folder to 'images'
            os.rename(obj_train_data_path, os.path.join(root, "images"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Move .txt files and rename folders")
    parser.add_argument("--input_folder", help="Path to the input folder")
    args = parser.parse_args()

    move_txt_files(args.input_folder)
