import os
import cv2
import sys
import numpy as np
import tensorflow as tf
from PIL import ImageGrab
from matplotlib import pyplot as plt
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

import time as delay
from multiprocessing import Process
from threading import Thread
import multiprocessing as mp
from plyer import notification
from datetime import datetime

cap = cv2.VideoCapture(1)
cap.set(3, 1280)
cap.set(4, 720)

count = 0
istream = False
permit_detect = True

image_save_path = "C:/Users/Public/Pictures/SP_Testing"
directory = "C:/Users/Public/Videos/SP_Vid_Testing"

if not os.path.isdir(image_save_path):
    os.mkdir(image_save_path)
if not os.path.isdir(directory):
    os.mkdir(directory)

# Path to frozen detection graph and label map.
MODEL_NAME = 'ssdlite_mobilenet_v2_coco_2018_05_09.pb'
LABEL_MAP_NAME = 'mscoco_complete_label_map.pbtxt'
PATH_TO_CKPT = os.path.join(os.curdir, 'frozen_models', MODEL_NAME)
PATH_TO_LABELS = os.path.join(os.curdir, 'label_maps', LABEL_MAP_NAME)

# Leave this in case a need to scale or add detections in the future
NUM_CLASSES = 1

# Load frozence inference model into memory
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.compat.v1.GraphDef()
    with tf.io.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')


# Load label map
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(
    label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)


# Load image helper function
def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)

def permit():

    global permit_detect
    delay.sleep(3)
    permit_detect = True


def offsetter():

    global count, istream  # Person counter variable, Stream checking variable
    global notif

    hasrecorded = False  # Checks if an image had already been recorded
    permit_detect = False

    delay.sleep(2)  # 2-second offset

    # Loop for recording
    while istream:
        if hasrecorded == False:
            count += 1

            notification.notify(
                title="DETECTION TEST",
                message=str(count) + " Detection(s) so Far!",
                app_icon="avs_icon.ico"
            )

        hasrecorded = True

def countdown():
    if __name__ == '__main__':
        offset = Thread(target=offsetter)
        offset.daemon = True
        offset.start()

def buffer():
    if __name__ == '__main__':
        allow = Thread(target=permit)
        allow.daemon = True
        allow.start()

# Detection loop
with detection_graph.as_default():
    with tf.compat.v1.Session(graph=detection_graph) as sess:
        while True:
            # Read frame from camera
            ret, image_np = cap.retrieve(cap.grab())
            # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
            image_np_expanded = np.expand_dims(image_np, axis=0)
            # Extract image tensor
            image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
            # Extract detection boxes
            boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
            # Extract detection scores
            scores = detection_graph.get_tensor_by_name('detection_scores:0')
            # Extract detection classes
            classes = detection_graph.get_tensor_by_name('detection_classes:0')
            # Extract number of detections
            num_detections = detection_graph.get_tensor_by_name(
                'num_detections:0')
            # Run the session to detect object
            (boxes, scores, classes, num_detections) = sess.run(
                [boxes, scores, classes, num_detections],
                feed_dict={image_tensor: image_np_expanded})
            # Simplify arrays
            boxes = np.squeeze(boxes)
            scores = np.squeeze(scores)
            classes = np.squeeze(classes)
            # Filter non-person detections
            indices = np.argwhere(classes == 1)
            boxes = np.squeeze(boxes[indices])
            scores = np.squeeze(scores[indices])
            classes = np.squeeze(classes[indices])

            # Draw boxes
            vis_util.visualize_boxes_and_labels_on_image_array(
                image_np,
                np.squeeze(boxes),
                np.squeeze(classes).astype(np.int32),
                np.squeeze(scores),
                category_index,
                use_normalized_coordinates=True,
                line_thickness=8)

            # Display output
            cv2.imshow('AVS', image_np)

            # Detection checkers
            if np.count_nonzero(boxes) > 0:
                if istream == False and permit_detect:
                    istream = True
                    countdown()
            else:
                istream = False
                if permit_detect == False:
                    buffer()

            if cv2.waitKey(25) & 0xFF == ord('q'):
                istream = False
                cv2.destroyAllWindows()
                break

sys.exit()