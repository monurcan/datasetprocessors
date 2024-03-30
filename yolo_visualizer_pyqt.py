"""
# python /mnt/RawPublicDatasets/USV/parsers/yolo_visualizer_as_video.py --im_folder /mnt/RawPublicDatasets/USV/data/images/ --txt_folder /mnt/RawPublicDatasets/USV/data/images/
# eğer txt_folder images -> labels replace
# find yaparsan istediginden buluyor
# q -> cikis
# f -> 1 frame ileri
# d -> 1 frame geri
# v -> 20 frame ileri
# c -> 20 frame geri
# x -> seçili bbox sil
# n -> n tuşlayınca bbox ekleme aktif oluyor, 2 kere tıklayarak bbox köşelerrini seçiyorsunuz cvattaki gibi. Sadece ilk tıklamada tıkladığınız yer görünmüyor. 2 tıklamada bbox görünür oluyor.
# o -> frame sil
# k -> frame kırp. k ya basıp 2 nokta seçince oluşturulan kutu kırpılıyor.
# + -> büyüt
# - -> küçült
# mouse_click -> selcet bbox (default hepsi seçili)
# bir sayiya basarsan seçili kutuların hepsini ona cevirir
"""
import argparse
import os

from natsort import natsorted
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QColor, QFont, QImage, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import (QApplication, QGraphicsPixmapItem, QGraphicsScene,
                             QGraphicsView, QLabel, QMainWindow)

# Command line argument parser
parser = argparse.ArgumentParser(
    description='YOLO Visualizer, Annotator, Cropper.')
parser.add_argument('--im_folder', type=str, required=True)
parser.add_argument('--txt_folder', type=str)
parser.add_argument('--labels', type=str,
                    default="vehicle,person,animal,herd,antitank")
parser.add_argument('--find', type=int)
args = parser.parse_args()

# HELPER FUNCTIONS


def print_progress(index, num_of_files, image_path):
    progress = f"Processing element {index+1} of {num_of_files} -> {image_path}"
    # truncate or pad progress string
    progress = progress[:progress_width-1].ljust(progress_width, ".")
    print(progress)


def list_files(path, ext):
    files_ = []
    for root, _, files in os.walk(path):
        for f in files:
            if f.lower().endswith(ext):
                files_.append(os.path.join(root, f))

    return natsorted(files_)


def update_txt_label(txt_path):
    # Update the txt file
    with open(txt_path, "w") as f:
        for box_data in box_info:
            f.write(
                f"{box_data[0]} {box_data[1]} {box_data[2]} {box_data[3]} {box_data[4]}\n")


def yolo_to_pyqt_coord(x_center, y_center, width, height, im_w, im_h):
    w, h = (width * im_w), (height * im_h)
    x, y = ((x_center * im_w) - w / 2), ((y_center * im_h) - h / 2)
    x1, y1, x2, y2 = (round(i) for i in [x, y, x + w, y + h])
    return x1, y1, x2, y2


def pyqt_to_yolo_coord(x1, y1, x2, y2, im_w, im_h):
    width, height = abs(x2-x1) / im_w, abs(y2-y1) / im_h
    x_center, y_center = (x1+x2)/(2*im_w), (y1+y2)/(2*im_h)
    return [x_center, y_center, width, height]


# INITIATLIZATIONS
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')
TERMINATE = -1
FIRST_INIT_IDX = -1
START_DRAWING_BBOX_BOOL = False
DEFAULT_BBOX_CLASS = 1
image_files = list_files(args.im_folder, IMAGE_EXTENSIONS)

if args.txt_folder is None:
    args.txt_folder = args.im_folder.replace('images', 'labels')

label_names = args.labels.split(',')
progress_width = 150
boxes = []
box_info = []
draw_bbox_coordinates = []
crop_coords = []  # ordered, x1,y1,x2,y2, x1<x2

# Initialize the main window and graphics view
app = QApplication([])
window = QMainWindow()
window.setWindowTitle("YOLO Visualizer")
scene = QGraphicsScene()
view = QGraphicsView(scene)
window.setCentralWidget(view)
pixmap_item = QGraphicsPixmapItem()
scene.addItem(pixmap_item)


# EVENT LISTENERS
# Mouse press event handler
def mousePressEvent(event):
    global txt_path, image_path, qimage, selected_index, draw_bbox_mode, crop_mode
    pos = view.mapToScene(event.pos())
    x = pos.x()
    y = pos.y()
    coord = [x, y]

    if draw_bbox_mode:
        draw_bbox_coordinates.extend(coord)
        if len(draw_bbox_coordinates) == 4:
            draw_bbox()
            draw_bbox_coordinates.clear()
            draw_bbox_mode = False
            app.quit()
    elif crop_mode:
        crop_coords.extend(coord)
        if len(crop_coords) == 4:
            # Swap x and y if necessary
            if crop_coords[0] > crop_coords[2]:
                crop_coords[0], crop_coords[2] = crop_coords[2], crop_coords[0]
            if crop_coords[1] > crop_coords[3]:
                crop_coords[1], crop_coords[3] = crop_coords[3], crop_coords[1]
            # Crop the image and adjust the bounding box coordinates
            crop_and_adjust()
            crop_coords.clear()
            crop_mode = False
            app.quit()
    else:
        # Create a list of all bounding boxes containing the click coordinates
        candidate_boxes = [(idx, box) for idx, box in enumerate(
            boxes) if box[0] <= x <= box[2] and box[1] <= y <= box[3]]

        if candidate_boxes:
            # Select the smallest bounding box
            selected_index, selected_box = min(candidate_boxes, key=lambda bb: (
                bb[1][2] - bb[1][0]) * (bb[1][3] - bb[1][1]))
            # Redraw the image_path
            draw_image()

# Mouse press event handler


def keyPressEvent(event):
    global txt_path, image_path, qimage, index, selected_index, draw_bbox_mode, crop_mode
    num_of_files = len(image_files)
    key = event.key()
    index_update = 0
    if key == Qt.Key_Q:
        # terminate the program.
        index = TERMINATE
        app.quit()
        return
    elif key == Qt.Key_N:
        # Toggle draw_bbox_mode
        draw_bbox_mode = not draw_bbox_mode
        return
    elif key == Qt.Key_K:
        # Toggle cropping mode
        crop_mode = not crop_mode
        crop_coords.clear()
        return  # no update
    elif key == Qt.Key_Plus:
        view.scale(1.3, 1.3)
        return  # no update
    elif key == Qt.Key_Minus:
        view.scale(1 / 1.3, 1 / 1.3)
        return  # no update
    elif key == Qt.Key_F:
        index_update = 1
    elif key == Qt.Key_D:
        index_update = -1
    elif key == Qt.Key_V:
        index_update = 20
    elif key == Qt.Key_C:
        index_update = -20
    elif key == Qt.Key_X:
        # delete only target box if selected.
        if selected_index != FIRST_INIT_IDX:
            del box_info[selected_index]
            update_txt_label(txt_path)
        else:
            return
    elif key == Qt.Key_O:
        index_update = 0
        try:
            os.remove(image_path)
            print("%s removed successfully" % image_path)
            del image_files[index]
        except OSError as error:
            print(error)
            print("File path can not be removed")
    elif key >= Qt.Key_0 and key <= Qt.Key_9:
        target_class = key - Qt.Key_0  # Convert key code to number
        if selected_index == FIRST_INIT_IDX:
            # change all
            for box_data in box_info:
                box_data[0] = target_class
        else:
            # change only target box.
            box_info[selected_index][0] = target_class
        # Update the txt file
        update_txt_label(txt_path)

    else:
        return  # no update
    index = (index + index_update) % num_of_files
    app.quit()


view.mousePressEvent = mousePressEvent
view.keyPressEvent = keyPressEvent


# VISUALIZERS
def draw_bbox():
    global qimage
    # update the box infos and update the txt files
    pyqt_coords_list = pyqt_to_yolo_coord(
        *draw_bbox_coordinates, qimage.width(), qimage.height())
    pyqt_bbox = [DEFAULT_BBOX_CLASS] + pyqt_coords_list
    box_info.append(pyqt_bbox)
    update_txt_label(txt_path)


def crop_and_adjust():
    global qimage, image_path, txt_path, box_info
    im_w_prev, im_h_prev = qimage.width(), qimage.height()
    x1, y1, x2, y2 = crop_coords
    cropped_qimage = qimage.copy(x1, y1, x2 - x1, y2 - y1)
    im_w_new, im_h_new = cropped_qimage.width(), cropped_qimage.height()

    new_box_info = []
    for box_data in box_info:
        label, x_center, y_center, width, height = box_data
        x1, y1, x2, y2 = yolo_to_pyqt_coord(
            x_center, y_center, width, height, im_w_prev, im_h_prev)
        x1 = x1 - crop_coords[0] if x1 >= crop_coords[0] else 0
        y1 = y1 - crop_coords[1] if y1 >= crop_coords[1] else 0
        x2 = x2 - \
            crop_coords[0] if x2 <= crop_coords[2] else (
                crop_coords[2] - crop_coords[0])
        y2 = y2 - \
            crop_coords[1] if y2 <= crop_coords[3] else (
                crop_coords[3] - crop_coords[1])
        new_yolo_coords = pyqt_to_yolo_coord(
            x1, y1, x2, y2, im_w_new, im_h_new)
        new_box_info.append([label] + new_yolo_coords)

    box_info = new_box_info
    print(box_info)
    qimage = cropped_qimage
    qimage.save(image_path)
    update_txt_label(txt_path)


# Draw image_path
def draw_image():
    global txt_path, image_path, qimage, selected_index, draw_bbox_mode, crop_mode
    draw_bbox_mode = False
    crop_mode = False
    pixmap = QPixmap.fromImage(qimage)
    painter = QPainter(pixmap)

    # Draw bounding boxes
    for idx, box in enumerate(boxes):
        x1, y1, x2, y2 = box
        label, _, _, _, _ = box_info[idx]
        color = QColor(255, 255, 0)  # dark red
        pensize = 2
        textsize = 5
        pen = QPen(color, pensize)  # bbox line color and width
        if selected_index != idx and selected_index != FIRST_INIT_IDX:
            pen = QPen(color, 1)
        painter.setPen(pen)
        painter.drawRect(x1, y1, x2 - x1, y2 - y1)
        painter.setFont(QFont("Helvetica", textsize))  # text style and width
        if not y1-pensize-textsize <= 0:
            painter.drawText(
                x1, y1-pensize, label_names[label % len(label_names)])
        else:
            painter.drawText(x1, y1+pensize+textsize,
                             label_names[label % len(label_names)])

    # Draw image_path filename
    # painter.setPen(QColor(255, 255, 255))
    # painter.setFont(QFont("Helvetica", 10))
    # painter.drawText(30, 30, image_path.split('/')[-1])
    window.setWindowTitle(image_path)

    painter.end()
    pixmap_item.setPixmap(pixmap)
    view.setSceneRect(QRectF(pixmap.rect()))
    view.fitInView(QRectF(pixmap.rect()), Qt.KeepAspectRatio)
    view.centerOn(pixmap_item)
    # window.setGeometrqy(window.geometry().x(), window.geometry().y(), pixmap.width(), pixmap.height())
    # Set the scaling factor for the view to 2
    view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
    view.setRenderHint(QPainter.Antialiasing)
    view.setRenderHint(QPainter.SmoothPixmapTransform)

    view.update()


def visualize_index():
    global txt_path, image_path, qimage, index, selected_index
    selected_index = FIRST_INIT_IDX
    boxes.clear()  # clear the previous boxes.
    box_info.clear()  # clear the previous boxes.
    image_path = image_files[index]
    num_of_files = len(image_files)
    print_progress(index, num_of_files, image_path)
    txt_path = os.path.splitext(image_path)[0]
    if args.txt_folder is not None:
        txt_path = os.path.join(args.txt_folder, txt_path.split('/')[-1])
        txt_path += ".txt"
    qimage = QImage(image_path)

    try:
        with open(txt_path, "r") as lines:
            for line in lines:
                coordinates = line.rstrip('\n').split(' ')
                label = int(coordinates[0])
                if args.find is not None:
                    if label != args.find:
                        continue
                x_center, y_center, width, height = [
                    float(x) for x in coordinates[1:]]
                x1, y1, x2, y2 = yolo_to_pyqt_coord(
                    x_center, y_center, width, height, qimage.width(), qimage.height())
                # Add box coordinates to the boxes list
                boxes.append([x1, y1, x2, y2])
                box_info.append([label, x_center, y_center, width, height])

        draw_image()
        window.show()
        app.exec_()

    except OSError:
        print("Could not open/read file:", txt_path)

        draw_image()
        window.show()
        app.exec_()


def visualize_yolo():
    global index
    index = 0
    while index != TERMINATE:
        visualize_index()


if __name__ == "__main__":
    visualize_yolo()
