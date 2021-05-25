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
from tkinter import messagebox
from validate_email import validate_email   # Needs Installation

# E-mail import
import yagmail                              # Needs Installation

# Background Notification imports
from plyer import notification              # Needs Installation

from pathlib import Path
from PIL import ImageGrab
from datetime import datetime
from matplotlib import pyplot as plt
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

# Stream Check Variable
istream = False
hasrecorded = True
count = 0

logged = True

#Variables for E-mail and Phone
project_address = "avs.detector.notif@gmail.com"
password = "avspy4121"

email = ""
directory = ""
phone_number = ""
image_save_path = ""

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

from user_db import Database

db = Database('users_log.db')

def disable():
    global is_custom

    is_custom = False
    vid_entry.delete(0, END)
    vid_entry.insert(0, "C:/Users/Public/Videos/avs_videos")
    vid_entry.configure(state=DISABLED)

def switch2():
    log.withdraw()
    window.deiconify()

def logger():

    global email, sms, directory, image_save_path
    user_info = db.login(user_entry.get(), pass_entry.get())

    if user_info == None:
        messagebox.showerror(title="Invalid input!", message="No User Found.")

    else:
        messagebox.showinfo(message="Login Successful!")
        email = user_info[1]
        sms = user_info[3]
        directory = user_info[4]
        image_save_path = user_info[5]
        print(email+" "+" "+sms+" "+directory+" "+image_save_path)
        log.destroy()
        window.destroy()

def switch():
    window.withdraw()

    global log, user_entry, pass_entry
    log = Toplevel()

    # Window Appearance
    log.title("Log In: Intruder Detection Application")
    log.geometry('260x125')
    log.wm_resizable(width='False', height='False')

    user_label = Label(log, text='Email', font=('bold', 10), padx=10, pady=10)
    user_label.grid(row=0, column=1, sticky=W)
    user_entry = Entry(log)
    user_entry.grid(row=0, column=2, sticky=W)

    pass_label = Label(log, text='Password', font=('bold', 10), padx=10, pady=15)
    pass_label.grid(row=1, column=1, sticky=W)
    pass_entry = Entry(log)
    pass_entry.grid(row=1, column=2, sticky=W)

    confirm = Button(log, text='Confirm', width=12, command=logger)
    confirm.grid(row=2, column=2, padx=15)

    back = Button(log, text='Back', width=12, command=switch2)
    back.grid(row=2, column=1, padx=15)

def input():
    # User Information
    global email, window, error, sms, phone_number, directory, image_save_path, is_custom
    global wait

    # Fetch User Data
    email = email_entry.get()
    password = password_entry.get()
    directory = vid_entry.get()
    image_save_path = vid_entry.get() + "/recorded_images"
    number = sms_entry.get()


    # Email Validation
    valid_mail = validate_email(email_address=email, check_format=True, check_blacklist=True, check_dns=True,
                                dns_timeout=10, check_smtp=True, smtp_timeout=10, smtp_helo_host='my.host.name',
                                smtp_from_address='my@from.addr.ess', smtp_debug=False)

    #Password Verification
    special_char = re.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,20}$")
    if re.search(special_char, password):
        valid_pass = True
    else:
        valid_pass = False

    # Phone Number Validation (feat. Google's Phone Number Library)
    try:
        if phonenumbers.parse(sms_entry.get()):
            sms = phonenumbers.parse(sms_entry.get())
            valid_sms = phonenumbers.is_valid_number(sms)
    except:
            valid_sms = False

    # Error Messages
    if not db.verify(email) == None:

        messagebox.showerror(message="Email Already Registered!")


    elif not os.path.isdir(directory):

        if is_custom:

          wait.destroy()

          # Creates Error Window
          messagebox.showerror(message="Directory does not Exist!")


        else:
            os.mkdir(directory)
            os.mkdir(image_save_path)


    elif not valid_mail:


        # Creates Error Window
        messagebox.showerror(message="Invalid Email Address!")


    elif not valid_pass:


        # Creates Error Window
        messagebox.showerror(message='Password must be 8 to 20 characters long and should\n '
                                        'contain at least one (1) digit, uppercase, and lowercase letter!')

    elif not valid_sms:

        # Creates Error Window
        messagebox.showerror(message="Invalid SMS Number!")


    else:
        db.signup(email, password, number, directory, image_save_path)
        phone_number = sms_entry.get() + "@sms.clicksend.com"
        messagebox.showinfo(title="Success!", message="Successfully Registered!")
        window.destroy()

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# GUI: User Prompt
window = Tk()

# Window Appearance
window.title("Sign Up: Intruder Detection Application")
window.geometry('330x275')
window.wm_resizable(width='False', height='False')

# Email Widgets
email_label = Label(window, text='Email Address', font=('bold',10), padx=10, pady=10)
email_label.grid(row=0, column=1, sticky=W)
email_entry = Entry(window)
email_entry.grid(row=0, column=2)

password_label = Label(window, text='Password', font=('bold',10), padx=10, pady=10)
password_label.grid(row=1, column=1, sticky=W)
password_entry = Entry(window)
password_entry.grid(row=1, column=2)

# SMS Widgets
country_code = StringVar()
sms_label = Label(window, text='Phone Number', font=('bold',10), padx= 10, pady=10)
sms_label.grid(row=2, column=1, sticky=W)
sms_entry = Entry(window, textvariable = country_code)
sms_entry.insert(0, "+63")
sms_entry.grid(row=2, column=2)

vid_dir = Label(window, text='Video Directory', font=('bold', 10), padx=10, pady=10)
vid_dir.grid(row=3, column=1, sticky=W)
vid_entry = Entry(window)
vid_entry.grid(row=3, column=2)

is_custom = True
custom = Radiobutton(window, text="Save to Public Videos Folder", command=disable, padx=10, pady=10)
custom.grid(row=4, column=1, sticky=W)

# Button
sign_up = Button(window, text='Sign Up', width=12, command=input)
sign_up.grid(row=5, column=2)

login = Button(window, text='Login', width=12, command=switch)
login.grid(row=5, column=1)

window.mainloop()

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
    video = cv2.VideoWriter(os.path.join(directory, 'VID_' + str(datestamp) + "_" + str(timestamp) + '.avi'), fourcc, 20.0, (1280, 720))

    # Loop for recording
    while istream and (int(delay.time() - start) < 60):

        # Frame Fetcher
        image = cv2.cvtColor(np.array(ImageGrab.grab(bbox=(0, 43, 1366, 686))), cv2.COLOR_BGR2RGB)
        video.write(image)

        # Image Recorder
        if hasrecorded == False:
            count += 1

            imgname = 'IMG' + str(datestamp) + "_" + str(timestamp) + '.jpg'
            cv2.imwrite(os.path.join(image_save_path, imgname), image)
            hasrecorded = True

            notif = thread.Thread(target=mailer, args=(imgname, dt))
            notif.daemon = True
            notif.start()

    # Video Finalizer
    video.release()

    delay.sleep(3)

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

            # Detection checkers
            if np.count_nonzero(boxes) > 0:
                if istream == False:
                    istream = True
                    countdown()
            else:
                istream = False

            if cv2.waitKey(25) & 0xFF == ord('q'):
                istream = False
                break

#Background Notification
notification.notify(
            title = "SUMMARY REPORT",
            message = str(count) + " Detections Made!",
            app_icon = "avs_icon.ico"
            )

# Kills all DAEMon-Flagged Threads
sys.exit()