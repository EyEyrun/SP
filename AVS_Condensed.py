import sys
import os, cv2
import pyautogui
import numpy as np
import time as delay
import tensorflow as tf
from threading import Thread

# Background Notification imports
from plyer import notification              # Needs Installation

from pathlib import Path
from PIL import ImageGrab
from datetime import datetime
from matplotlib import pyplot as plt
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Function that recalls the offset thread whenever a detection has occurred
def countdown():

    global key, count, istream, offset

    # Thread initializers

    offset = Thread(target=offsetter)
    offset.daemon = True
    offset.start()

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Performs the 2-sec. offset and recording functions in another thread.
def offsetter():

    global count, istream   # Person counter variable, Stream checking variable
    global notif

    hasrecorded = False     # Checks if an image had already been recorded

    delay.sleep(2)          # 2-second offset

    start = delay.time()    # Benchmarks with timestamp for the 60-sec. recording

    dt = datetime.now()     # Gets exact date and time for naming records
    datestamp = int(dt.strftime("%Y%m%d"))  #Naming (Date)
    timestamp = int(dt.strftime("%H%M%S"))  #Naming (Time)

    # Loop for recording
    while istream and (int(delay.time() - start) < 60):

        # Frame Fetcher
        frame = pyautogui.screenshot()
        image = np.array(frame)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Image Recorder
        if hasrecorded == False:

            count += 1

            imgname = 'IMG' + str(datestamp) + "_" + str(timestamp) + '.jpg'
            cv2.imwrite(os.path.join(image_save_path, imgname), image)
            hasrecorded = True

        notification.notify(
            title="DETECTION TEST",
            message=str(count) + " Detection(s) so Far!",
            app_icon="avs_icon.ico"
        )

    delay.sleep(3)

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Load image helper function
def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Stream Check Variable
istream = False
hasrecorded = True
count = 0

image_save_path = "C:/Users/Public/Pictures/SP_Testing"

if not os.isdir(image_save_path):
    os.mkdir(image_save_path)

# Set screen size for Screen Recording
screen_size = pyautogui.size()

# Set Display for turning off Program
icon = cv2.imread("AVS Show.jpg")

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Path to frozen detection graph and label map.
MODEL_NAME = 'ssdlite_mobilenet_v2_coco_2018_05_09.pb'
LABEL_MAP_NAME = 'mscoco_complete_label_map.pbtxt'
PATH_TO_CKPT = os.path.join(os.curdir, 'frozen_models', MODEL_NAME)
PATH_TO_LABELS = os.path.join(os.curdir, 'label_maps', LABEL_MAP_NAME)

# Leave this in case a need to scale or add detections in the future
NUM_CLASSES = 1

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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

# Detection loop
with detection_graph.as_default():
    with tf.compat.v1.Session(graph=detection_graph) as sess:
        while True:
            # Read frame from camera
            img = ImageGrab.grab(bbox=(0, 43, 1366, 686))
            image_np = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
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

            cv2.imshow("(Minimize Me) Press Q to Exit", icon)

            # Detection checkers
            if np.count_nonzero(boxes) > 0:
                if istream == False:
                    istream = True
                    countdown()
            else:
                istream = False

            if cv2.waitKey(1) == ord("q"):
                cv2.destroyAllWindows()
                istream = False
                break

#Background Notification
notification.notify(
            title = "DETECTION REPORT",
            message = "A Total of " + str(count) + " Detections Made!",
            app_icon = "avs_icon.ico"
            )

# Kills all DAEMon-Flagged Threads
sys.exit()