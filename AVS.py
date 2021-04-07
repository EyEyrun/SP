import os, cv2
import numpy as np
import time as delay
import tensorflow as tf
import threading as thread

# E-mail MIME imports
import yagmail

from pathlib import Path
from datetime import datetime
from matplotlib import pyplot as plt
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util


# Define the video stream.
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Save Directories
image_save_path = "avs_images"
video_save_path = "avs_videos"

# Stream Check Variable
istream = False
hasrecorded = True
count = 0

# Path to frozen detection graph and label map.
MODEL_NAME = 'ssdlite_mobilenet_v2_coco_2018_05_09.pb'
LABEL_MAP_NAME = 'mscoco_complete_label_map.pbtxt'
PATH_TO_CKPT = os.path.join(os.curdir, 'frozen_models', MODEL_NAME)
PATH_TO_LABELS = os.path.join(os.curdir, 'label_maps', LABEL_MAP_NAME)

# Leave this in case a need to scale or add detections in the future
NUM_CLASSES = 1

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Startup functions, directories are checked/created upon running.
if not os.path.isdir(video_save_path):
    os.mkdir(video_save_path)

if not os.path.isdir(image_save_path):
    os.mkdir(image_save_path)

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#Variables for E-mail
project_address = "avs.detector.notif@gmail.com"
user_address = "ajsenar@gmail.com"
password = "avspy4121"

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

# Load image helper function
def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Performs Email Notification
def mailer(name, timestamp):

    stamp = timestamp.strftime("%B %d, %Y - %I:%M %p")

    msg = yagmail.SMTP(project_address, password)
    msg.send(
        to = user_address,
        subject = "Alert!",
        contents = "Intruder detected at " + stamp,
        attachments = os.path.join(image_save_path, name)
    )
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Performs the 2-sec. offset and recording functions in another thread.
def offsetter():

    global count, istream   # Person counter variable, Stream checking variable
    hasrecorded = False     # Checks if an image had already been recorded

    delay.sleep(2)          # 2-second offset
    start = delay.time()    # Benchmarks with timestamp for the 60-sec. recording

    dt = datetime.now()     # Gets exact date and time for naming records
    datestamp = int(dt.strftime("%Y%m%d"))  #Naming (Date)
    timestamp = int(dt.strftime("%H%M%S"))  #Naming (Time)

    # Video initialization functions
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video = cv2.VideoWriter(os.path.join(video_save_path, 'VID_' + str(datestamp) + "_" + str(timestamp) + '.avi'), fourcc, 20.0, (1280, 720))

    # Loop for recording
    while istream and (int(delay.time() - start) < 60):

        # Frame getter
        return_value, image = cap.read()
        video.write(image)

        # Image recorder
        if hasrecorded == False:
            count += 1
            print("Person " + str(count) + " found!")
            imgname = 'IMG' + str(datestamp) + "_" + str(timestamp) + '.jpg'
            cv2.imwrite(os.path.join(image_save_path, imgname), image)
            hasrecorded = True

            notif = thread.Thread(target=mailer, args=(imgname, dt))
            notif.start()

    # Video finalizer
    video.release()


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Function that re-calls the offset thread whenever a detection has occured
def countdown():

    global key, count, istream

    # Thread initializers
    event = thread.Event()
    offset = thread.Thread(target=offsetter)
    offset.start()

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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
                if istream == False:
                    istream = True
                    countdown()
            else:
                istream = False

            if cv2.waitKey(25) & 0xFF == ord('q'):
                istream = False
                cv2.destroyAllWindows()
                break