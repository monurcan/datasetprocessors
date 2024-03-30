import argparse
import os

import cv2
from natsort import natsorted


def concatenate_and_convert(input_dir, file_extension, output_path, frame_rate):
    # Find and sort files
    files = natsorted(
        [f for f in os.listdir(input_dir) if f.endswith("." + file_extension)]
    )

    # Generate a list of file paths
    file_paths = [os.path.join(input_dir, f) for f in files]

    # Get the first image to get dimensions
    first_image = cv2.imread(file_paths[0])
    height, width, layers = first_image.shape

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # You can change the codec as needed
    video = cv2.VideoWriter(output_path, fourcc, frame_rate, (width, height))

    # Write frames to the video
    for file_path in file_paths:
        frame = cv2.imread(file_path)
        video.write(frame)

    # Release the video writer
    video.release()


# Example usage:
if __name__ == "__main__":
    # argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_dir",
        help="Input directory",
        default="/home/kilavuz_dev/workspace/ida/outputs_cvimshow_gt_bear",
    )
    parser.add_argument("--file_extension", help="File extension", default="jpg")
    parser.add_argument(
        "--output_path",
        help="Output path",
        default="/home/kilavuz_dev/workspace/ida/outputs_cvimshow_deep_new_2oct.mp4",
    )
    parser.add_argument("--frame_rate", help="Frame rate", type=int, default=14)
    args = parser.parse_args()

    concatenate_and_convert(
        args.input_dir, args.file_extension, args.output_path, args.frame_rate
    )
