import argparse
import os
import cv2
import numpy as np
import shutil
from multiprocessing import Pool
from functools import partial
from typing import List
from abc import ABC, abstractmethod
from tqdm import tqdm
from collections import deque, OrderedDict

class ImageLoader:
    @staticmethod
    def load_image(file_path):
        frame = cv2.imread(file_path)
        assert frame is not None, f'Image Not Found {file_path}'
        return frame

class AbstractCuboidFormation(ABC):
    def __init__(self, image_paths: List[str]):
        self.image_paths = image_paths
    
    @abstractmethod
    def get_cuboid(self, i: int) -> np.ndarray:
        pass

class CuboidFormation(AbstractCuboidFormation):
    def __init__(self, image_paths: List[str], cuboid_length: int = 4, cuboid_sampling: int = 10, max_loaded_images: int = 100):
        super().__init__(image_paths)
        self.cuboid_length = cuboid_length
        self.cuboid_sampling = cuboid_sampling
        self.dataset_length = len(self.image_paths)
        
        self.max_loaded_images = self.cuboid_sampling * self.cuboid_length * 8
        self.loaded_images = OrderedDict()

    def get_cuboid(self, i: int) -> np.ndarray:
        frame_cuboid = []
        w, h = None, None

        for j in range(self.cuboid_length):
            image_path = self.image_paths[i - j * self.cuboid_sampling % self.dataset_length]

            if image_path in self.loaded_images:
                frame = self.loaded_images[image_path]
            else:
                frame = ImageLoader.load_image(image_path)
                if len(self.loaded_images) >= self.max_loaded_images:
                    self.loaded_images.popitem(last=False)  # Remove the oldest entry

                self.loaded_images[image_path] = frame

            w = w or frame.shape[1]
            h = h or frame.shape[0]

            if w is not None and h is not None:
                frame = cv2.resize(frame, (w, h))

            frame_cuboid.append(frame)

        return np.array(frame_cuboid)

class AbstractImageProcessor(ABC):
    @abstractmethod
    def process_images(self, frame_cuboid: np.ndarray) -> np.ndarray:
        pass

class MotionExtractProcessor(AbstractImageProcessor):
    def __init__(self, threshold=30, energy_threshold=2.8, blur_kernel=(15, 15)):
        self.threshold = threshold
        self.energy_threshold = energy_threshold
        self.blur_kernel = blur_kernel

    def convert_to_grayscale(self, frame):
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def compute_frame_diff(self, frame_t, frame_t_1, frame_t_2):
        frame_t_gray = self.convert_to_grayscale(frame_t)
        frame_t_1_gray = self.convert_to_grayscale(frame_t_1)
        frame_t_2_gray = self.convert_to_grayscale(frame_t_2)

        frame_diff_1 = cv2.absdiff(frame_t_gray, frame_t_1_gray)
        frame_diff_2 = cv2.absdiff(frame_t_gray, frame_t_2_gray)

        frame_diff = cv2.bitwise_and(frame_diff_1, frame_diff_2)

        _, frame_diff = cv2.threshold(frame_diff, self.threshold, 255, cv2.THRESH_BINARY)

        frame_diff_total_energy = np.mean(frame_diff)
        if frame_diff_total_energy > self.energy_threshold:
            frame_diff = frame_diff * 0.0

        frame_diff = cv2.GaussianBlur(frame_diff, self.blur_kernel, 0)

        return frame_diff

    def process_images(self, frame_cuboid: np.ndarray) -> np.ndarray:
        frame_diff = self.compute_frame_diff(frame_cuboid[0], frame_cuboid[1], frame_cuboid[2])[..., np.newaxis]
        frame_diff_1 = self.compute_frame_diff(frame_cuboid[0], frame_cuboid[2], frame_cuboid[3])[..., np.newaxis]

        frame_cuboid_t = frame_cuboid[0]

        processed_image = np.concatenate((frame_cuboid_t.astype(float), frame_diff_1.astype(float), frame_diff.astype(float)),
                                         axis=-1)

        return processed_image

class ImageSaver(ABC):
    @abstractmethod
    def _save(self, save_file_path, image):
        pass
    
    def save_image(self, processed_image, img_path, base_path, save_path):
        rel_path = os.path.relpath(img_path, base_path)
        save_file_path = os.path.join(save_path, rel_path)
        os.makedirs(os.path.dirname(save_file_path), exist_ok=True)
        
        self._save(save_file_path, processed_image)
        
    @staticmethod
    def copy_label_files(img_paths, base_path, save_path):
        for img_path in img_paths:
            label_path = ImageSaver.img2label_path(img_path, base_path)
            rel_label_path = os.path.relpath(label_path, base_path)
            save_label_path = os.path.join(save_path, rel_label_path)
            os.makedirs(os.path.dirname(save_label_path), exist_ok=True)
            if os.path.exists(label_path):
                shutil.copy2(label_path, save_label_path)

    @staticmethod
    def img2label_path(img_path, base_path):
        sa, sb = f'{os.sep}images{os.sep}', f'{os.sep}labels{os.sep}'  # /images/, /labels/ substrings
        return sb.join(img_path.rsplit(sa, 1)).rsplit('.', 1)[0] + '.txt'

class NPYImageSaver(ImageSaver):
    def _save(self, save_file_path, image):
        np.save(save_file_path, image)

class CVImageSaver(ImageSaver):
    def _save(self, save_file_path, image):
        cv2.imwrite(save_file_path, image)

class ImageProcessingPipeline:
    def __init__(self, image_processor: AbstractImageProcessor, cuboid_formation: AbstractCuboidFormation, image_saver: ImageSaver, image_paths: List[str]):
        self.image_processor = image_processor
        self.cuboid_formation = cuboid_formation
        self.image_saver = image_saver
        self.image_paths = image_paths

    def process_image_batch(self, img_path_indices, base_path, save_path):
        for i in tqdm(img_path_indices):            
            # Skip if file already exists
            # rel_path = os.path.relpath(self.image_paths[i], base_path)
            # save_file_path = os.path.join(save_path, rel_path)
            # if os.path.exists(save_file_path):
            #     continue
            #

            frame_cuboid = self.cuboid_formation.get_cuboid(i)
            processed_image = self.image_processor.process_images(frame_cuboid)
            self.image_saver.save_image(processed_image, self.image_paths[i], base_path, save_path)
            self.image_saver.copy_label_files([self.image_paths[i]], base_path, save_path)

    def process_images_multiprocessing(self, base_path: str, save_path: str):
        # Divide image_paths into chunks for multiprocessing
        num_chunks = 1
        image_paths_chunks = [list(range(i, i + num_chunks)) for i in range(0, len(image_paths), num_chunks)]

        with Pool() as pool, tqdm(total=len(image_paths)) as pbar:
            process_partial = partial(self.process_image_batch, base_path=base_path, save_path=save_path)
            for _ in pool.imap_unordered(process_partial, image_paths_chunks):
                pbar.update(1)
                
    def process_images(self, base_path: str, save_path: str):
        self.process_image_batch(list(range(len(self.image_paths))), base_path, save_path)
        

def parse_args():
    parser = argparse.ArgumentParser(description='Image Processing Script')
    parser.add_argument('--images_txt_path', type=str, help='Path to the text file containing image paths')
    parser.add_argument('--base_path', type=str, help='Prefix of each image path')
    parser.add_argument('--save_path', type=str, help='New save directory for processed images')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    image_paths = [line.strip() for line in open(args.images_txt_path, 'r')]

    motion_extract_processor = MotionExtractProcessor()
    cuboid_formation = CuboidFormation(image_paths)
    image_saver = NPYImageSaver()
    image_processing_pipeline = ImageProcessingPipeline(motion_extract_processor, cuboid_formation, image_saver, image_paths)

    image_processing_pipeline.process_images(args.base_path, args.save_path)
