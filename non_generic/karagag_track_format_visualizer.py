import os
import cv2
import json
import argparse
from natsort import natsorted

classIDColors = {
    0: (255, 0, 0), # blue - vehicle
    1: (0, 255, 0), # green - person
    2: (0, 0, 255), # red - animal
    3: (0, 255, 255), # yellow - herd
    10: (255, 255, 255) # white - change
}

# Function to process a single annotation file
def process_annotation_file(annotation_path, image_folder, window_name):
    # Load the JSON file
    with open(annotation_path) as json_file:
        data = json.load(json_file)
        
    # Get the image filename
    image_filename = os.path.splitext(os.path.basename(annotation_path))[0] + '.png'
    image_path = os.path.join(image_folder, image_filename)

    # Display the image with the bounding box
    image = cv2.imread(image_path)
    
    # If there are bounding boxes
    if data['json_vec']:
        # Read the camera FOV dimensions
        fov_height = data['json_vec'][0]['camera_fov']['height']
        fov_width = data['json_vec'][0]['camera_fov']['width']

        # Iterate over the bounding box annotations
        for annotation in data['json_vec']:
            # Read the bounding box coordinates
            x_offset = annotation['camera_fov']['x']
            y_offset = annotation['camera_fov']['y']
            x = annotation['rect']['x']
            y = annotation['rect']['y']
            width = annotation['rect']['width']
            height = annotation['rect']['height']

            # Calculate the actual bounding box coordinates
            x1 = int(x - x_offset - width / 2)
            y1 = int(y - y_offset - height / 2)
            x2 = int(x1 + width)
            y2 = int(y1 + height)

            # Get class ID
            class_ID = annotation['classID']

            cv2.rectangle(image, (x1, y1), (x2, y2), classIDColors[class_ID], 1)  # Draw the bounding box
        
    cv2.imshow(window_name, image)
    # cv2.imwrite("/mnt/onurcan/track_visualizer/kgag_cekim_17_05_22--xenics--Gece--1800m--2145-1/onurcan_video/"+image_filename, image)
    cv2.waitKey(0)

if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Bounding Box Visualizer')
    parser.add_argument('--annotation-folder', required=True, help='Path to the annotation folder')
    parser.add_argument('--image-folder', required=True, help='Path to the image folder')
    args = parser.parse_args()

    # Folder paths
    annotation_folder = args.annotation_folder
    image_folder = args.image_folder

    # Create a named window
    window_name = 'Bounding Box Visualizer'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    # Iterate over the annotation files in the folder
    for filename in natsorted(os.listdir(annotation_folder)):
        if filename.endswith('.json'):
            annotation_path = os.path.join(annotation_folder, filename)
            process_annotation_file(annotation_path, image_folder, window_name)
        
    cv2.destroyAllWindows()
