import sys
import os, cv2
import numpy as np
import time as delay
import tensorflow as tf
import threading as thread

# User Prompt imports
import socket
import phonenumbers                         # Needs Installation
from tkinter import *
from validate_email import validate_email   # Needs Installation

# E-mail import
import yagmail                              # Needs Installation

# Background Notification imports
from plyer import notification              # Needs Installation

from pathlib import Path
from datetime import datetime
from matplotlib import pyplot as plt
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

# Stream Check Variable
istream = False
hasrecorded = True
count = 0

# Save Directories
image_save_path = "avs_images"
video_save_path = "avs_videos"

#Variables for E-mail and Phone
project_address = "avs.detector.notif@gmail.com"
password = "avspy4121"
phone_number = ""
email = ""

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Startup functions, directories are checked/created upon running.
if not os.path.isdir(video_save_path):
    os.mkdir(video_save_path)

if not os.path.isdir(image_save_path):
    os.mkdir(image_save_path)

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def validate():
    # Validates within another Thread
    global prompt
    prompt = thread.Thread(target = input)
    prompt.daemon = True
    prompt.start()

def withdraw():
    global error
    error.destroy()

def input():
    # User Information
    global ip, email, window, error, sms, phone_number
    global waiting

    # Wait Notification Window
    wait = Toplevel()
    wait.columnconfigure(0, weight=1)
    wait.geometry("290x100")
    wait.title("Validating")
    wait.wm_resizable(width='False', height='False')
    wait_label = Label(wait, text='Validating information, please wait...', font=('bold', 10), padx=30, pady=30)
    wait_label.grid(row=0, column=0, sticky=W)
    wait.deiconify()


    # Fetch User Data
    email = email_entry.get()
    ip = ip_entry.get()

    # Phone Number Validation (feat. Google's Phone Number Library)
    try:
        if phonenumbers.parse(sms_entry.get()):
            sms = phonenumbers.parse(sms_entry.get())
            valid_sms = phonenumbers.is_valid_number(sms)
    except:
            valid_sms = False

    # Email Validation
    valid_mail = validate_email(email_address=email, check_format=True, check_blacklist=True, check_dns=True,
                                dns_timeout=10, check_smtp=True, smtp_timeout=10, smtp_helo_host='my.host.name',
                                smtp_from_address='my@from.addr.ess', smtp_debug=False)

    # IP Validation
    try:
        if socket.inet_aton(ip):
            valid_ip = True
    except:
            valid_ip = False

    # Checking All Info
    if valid_mail and valid_ip and valid_sms:
        phone_number = sms_entry.get() + "@sms.clicksend.com"
        wait.destroy()
        window.destroy()

    elif not(valid_mail):

        wait.destroy()

        # Creates Error Window
        error = Toplevel()
        error.columnconfigure(0, weight=1)
        error.geometry("150x100")
        error.title("Error")
        error.wm_resizable(width='False', height='False')

        error_label = Label(error, text='Invalid Email Address!', font=('bold',10), padx=30, pady=10)
        error_label.grid(row=0, column=0, sticky=W)
        ok = Button(error, text='OK', width=12, command=withdraw)
        ok.grid(row=1, column=0)
        error.deiconify()

    elif not(valid_ip):

        wait.destroy()

        # Creates Error Window
        error = Toplevel()
        error.columnconfigure(0, weight=1)
        error.geometry("150x100")
        error.title("Error")
        error.wm_resizable(width='False', height='False')

        error_label = Label(error, text='Invalid IP Address!', font=('bold', 10), padx=30, pady=10)
        error_label.grid(row=0, column=0, sticky=W)
        ok = Button(error, text='OK', width=12, command=withdraw)
        ok.grid(row=1, column=0)
        error.deiconify()

    elif not(valid_sms):

        wait.destroy()

        # Creates Error Window
        error = Toplevel()
        error.columnconfigure(0, weight=1)
        error.geometry("150x100")
        error.title("Error")
        error.wm_resizable(width='False', height='False')

        error_label = Label(error, text='Invalid SMS number!', font=('bold', 10), padx=30, pady=10)
        error_label.grid(row=0, column=0, sticky=W)
        ok = Button(error, text='OK', width=12, command=withdraw)
        ok.grid(row=1, column=0)
        error.deiconify()


#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# GUI: User Prompt
window = Tk()

# Window Appearance
window.title("Intruder Detection Application Prompt")
window.geometry('260x225')
window.wm_resizable(width='False', height='False')

# Email Widgets
email_label = Label(window, text='Email Address', font=('bold',10), padx=10, pady=20)
email_label.grid(row=0, column=1, sticky=W)
email_entry = Entry(window)
email_entry.grid(row=0, column=2)

# IP Widgets
ip_label = Label(window, text='IP Address', font=('bold',10), padx= 10, pady=20)
ip_label.grid(row=1, column=1, sticky=W)
ip_entry = Entry(window)
ip_entry.grid(row=1, column=2)

# SMS Widgets
country_code = StringVar()
sms_label = Label(window, text='Phone Number', font=('bold',10), padx= 10, pady=20)
sms_label.grid(row=2, column=1, sticky=W)
sms_entry = Entry(window, textvariable = country_code)
sms_entry.insert(0, "+63")
sms_entry.grid(row=2, column=2)

# Button
enter = Button(window, text='Confirm', width=12, command=validate)
enter.grid(row=3, column=2)

window.mainloop()

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Define the video stream.
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

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

# Load image helper function
def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Performs Email Notification
def mailer(name, timestamp):

    stamp = timestamp.strftime("%B %d, %Y - %I:%M %p") # Timestamp in String

    msg = yagmail.SMTP(project_address, password)
    msg.send(                                           # Mail to User Address
        to = email,
        subject = "Alert!",
        contents = "Intruder detected at " + stamp,
        attachments = os.path.join(image_save_path, name)
    )
    msg.send(                                           # Routing Message to SMS thru Email
        to=phone_number,
        subject="Alert!",
        contents="Intruder detected at " + stamp)

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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

    # Video initialization functions
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video = cv2.VideoWriter(os.path.join(video_save_path, 'VID_' + str(datestamp) + "_" + str(timestamp) + '.avi'), fourcc, 20.0, (1280, 720))

    # Loop for recording
    while istream and (int(delay.time() - start) < 60):

        # Frame Fetcher
        return_value, image = cap.read()
        video.write(image)

        # Image Recorder
        if hasrecorded == False:
            count += 1

            #Background Notification
            notification.notify(
                title = "DETECTION",
                message = str(count) + " Person(s) Found!",
                app_icon = "avs_icon.ico"
            )

            imgname = 'IMG' + str(datestamp) + "_" + str(timestamp) + '.jpg'
            cv2.imwrite(os.path.join(image_save_path, imgname), image)
            hasrecorded = True

            notif = thread.Thread(target=mailer, args=(imgname, dt))
            notif.daemon = True
            notif.start()

    # Video Finalizer
    notif.join()
    video.release()


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Function that re-calls the offset thread whenever a detection has occured
def countdown():
    global key, count, istream, offset

    # Thread initializers
    event = thread.Event()
    offset = thread.Thread(target=offsetter)
    offset.daemon = True
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

# Kills all DAEMon-Flagged Threads
sys.exit()