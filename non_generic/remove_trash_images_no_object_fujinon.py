from pathlib import Path

from PIL import Image

# files_path = "/mnt/RawInternalDatasets/karagag/Fujinon/VK/no_object/images"
files_path = "/mnt/RawInternalDatasets/karagag/Fujinon/VK/no_object_2/images"

for path in sorted(Path(files_path).rglob('*.png')):
    im = Image.open(path)
    width, height = im.size

    if width != 1920 or height != 1080:
        print("removing")
        path.unlink()
        print(path)
        print(width)
        print(height)
