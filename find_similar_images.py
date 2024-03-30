from tqdm import tqdm
from abc import ABC, abstractmethod
import argparse
import os
import cv2
from skimage.metrics import structural_similarity as ssim
from multiprocessing import Pool
from natsort import natsorted

class Image(ABC):
    @abstractmethod
    def load(self):
        pass

class OpenCVImage(Image):
    def __init__(self, path):
        self.path = path

    def load(self):
        image_data = cv2.imread(self.path)
        if image_data is None:
            raise ValueError(f"Error: Unable to read the image at '{self.path}'.")
        return image_data

class ImageComparator(ABC):
    @abstractmethod
    def is_similar(self, target_image, compare_image):
        pass

class SSIMImageComparator(ImageComparator):
    def __init__(self, threshold=0.8):
        self.threshold = threshold

    def calculate_ssim(self, img1, img2):
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        score, _ = ssim(gray1, gray2, full=True)
        return score

    def is_similar(self, target_image, compare_image):
        similarity_score = self.calculate_ssim(target_image.load(), compare_image.load())
        return similarity_score > self.threshold

class ImageFinder(ABC):
    @abstractmethod
    def find_images(self, folder_path):
        pass

class FilesystemImageFinder(ImageFinder):
    SUPPORTED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']

    def find_images(self, folder_path):
        for root, _, files in os.walk(folder_path):
            for file in natsorted(files):
                if any(file.lower().endswith(ext) for ext in self.SUPPORTED_EXTENSIONS):
                    yield OpenCVImage(os.path.join(root, file))

def compare_images(args):
    target_image, compare_image, image_comparator = args
    return compare_image.path if image_comparator.is_similar(target_image, compare_image) else None

class ImageProcessor:
    def __init__(self, image_comparator, image_finder):
        self.image_comparator = image_comparator
        self.image_finder = image_finder

    def find_similar_images(self, target_image, folder_path):
        with Pool() as pool:
            args_list = [(target_image, img, self.image_comparator) for img in self.image_finder.find_images(folder_path)]
            results = list(tqdm(pool.imap(compare_images, args_list), total=len(args_list), desc="Comparing images", unit="image"))

        return (result for result in results if result is not None)

def run_app(args):
    if not args.image_path or not args.folder:
        print("Error: Both --image_path and --folder are required.")
        return

    target_image = OpenCVImage(args.image_path)
    image_comparator = SSIMImageComparator()
    
    image_processor = ImageProcessor(image_comparator, FilesystemImageFinder())
    similar_images = image_processor.find_similar_images(target_image, args.folder)

    if similar_images:
        print("Similar Images:")
        for image_path in similar_images:
            print(image_path)
    else:
        print("No similar images found.")

def parse_args():
    parser = argparse.ArgumentParser(description='Find similar images in a folder to a given image.')
    parser.add_argument('--image_path', type=str, help='Path to the target image.')
    parser.add_argument('--folder', type=str, help='Path to the folder containing images to compare.')
    return parser.parse_args()

def main():
    args = parse_args()
    run_app(args)

if __name__ == "__main__":
    main()
