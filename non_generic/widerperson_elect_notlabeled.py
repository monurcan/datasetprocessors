import os
import shutil
from pathlib import Path

images_path = "/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/WiderPerson_ArabalarVarTemizlenmeliKULLANMA/WiderPerson/images"
images_notlabeled_path = "/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/WiderPerson_ArabalarVarTemizlenmeliKULLANMA/WiderPerson/images_notlabeled"
labels_path = "/mnt/RawInternalDatasets/KaraGAG/Fujinon/FromWeb/WiderPerson_ArabalarVarTemizlenmeliKULLANMA/WiderPerson/labels"

all_labels = [file.stem for file in sorted(Path(labels_path).rglob('*.txt'))]
all_images = [file.stem for file in sorted(Path(images_path).rglob('*'))]

# print(all_labels)
# print(all_images)
not_labeled_images = [image for image in all_images if image not in all_labels]

print(len(not_labeled_images))
for not_labeled in not_labeled_images:
    img_path = os.path.join(images_path, not_labeled)
    not_labeled_path = os.path.join(images_notlabeled_path, not_labeled)
    # print(img_path)
    # print(not_labeled_path)

    shutil.move(img_path, not_labeled_path)
