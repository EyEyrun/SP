import sys
import shutil
import bcrypt
import yagmail                              
import os, cv2
import numpy as np
import phonenumbers                         
import time as delay
import tensorflow as tf

from tkinter import *
from pathlib import Path
from user_db import Database
from threading import Thread
from datetime import datetime
from pyisemail import is_email              
from tkinter import messagebox
from plyer import notification              
from matplotlib import pyplot as plt
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#Functions for GUI

def cloak(e):
    password_label["text"] = "Password"
    password_entry.configure(show="*")

def uncloak(e):
    password_label["text"] = "Check Password"
    password_entry.configure(show="")

def l_cloak(e):
    pass_label["text"] = "Password"
    pass_entry.configure(show="*")

def l_uncloak(e):
    pass_label["text"] = "Check Password"
    pass_entry.configure(show="")

def insert():
    global is_custom

    is_custom = False
    vid_entry.delete(0, END)
    vid_entry.insert(0, "C:/Users/Public/Videos/avs_videos")

def switch2():

    log.withdraw()
    window.deiconify()

def logger():

    global email, sms, directory, image_save_path, capture

    pass_code = bytes(pass_entry.get(), encoding='utf-8')
    user_info = db.verify(user_entry.get())

    if user_info == None:
        messagebox.showerror(title="Invalid input!", message="No User Found.")

    elif not bcrypt.checkpw(pass_code, user_info[2]):
    	messagebox.showerror(title="Invalid Password!", message="Incorrect Password.")

    else:
        email = user_info[1]
        sms = user_info[3] + "@sms.clicksend.com"
        directory = user_info[4]
        image_save_path = user_info[5]
        capture = logcamnum.get()

        log.destroy()
        window.destroy()

def switch():

    window.withdraw()

    global log, user_entry, pass_entry, pass_label, logcamnum
    log = Toplevel()

    logcam = [0, 1, 2, 3, 4]

    # Window Appearance
    log.title("Login: Intruder Detection Application")
    log.geometry('260x140')
    log.wm_resizable(width='False', height='False')

    user_label = Label(log, text='Email', font=('bold', 10), padx=10, pady=5)
    user_label.grid(row=0, column=1, sticky=W)
    user_entry = Entry(log)
    user_entry.grid(row=0, column=2, sticky=W)

    pass_label = Label(log, text='Password', font=('bold', 10), padx=10, pady=5)
    pass_label.grid(row=1, column=1, sticky=W)
    pass_label.bind("<Enter>", l_uncloak)
    pass_label.bind("<Leave>", l_cloak)

    pass_entry = Entry(log, show="*")
    pass_entry.grid(row=1, column=2, sticky=W)

    logcam_label = Label(log, text='Camera', font=('bold', 10), padx=10, pady=5)
    logcam_label.grid(row=2, column=1, sticky=W)

    logcamnum = IntVar(log)
    logcamnum.set(cam[0])

    logcam_select = OptionMenu(log, logcamnum, *logcam)
    logcam_select.grid(row=2, column=2, sticky=W)

    confirm = Button(log, text='Confirm', width=12, command=logger)
    confirm.grid(row=3, column=2, padx=15, pady=10)

    back = Button(log, text='Back', width=12, command=switch2)
    back.grid(row=3, column=1, padx=15, pady=10)

    log.iconbitmap("avs_icon.ico")

def input():

    # User Information Variables
    global email, sms, directory, image_save_path, is_custom
    global diskfree, diskused, disktotal, capture

    # Fetch User Data
    email = email_entry.get()
    password = password_entry.get()
    number = sms_entry.get()
    directory = vid_entry.get()
    image_save_path = vid_entry.get() + "/recorded_images"
    duplicate_mail = True

    # Email Duplicate Validation
    if db.verify(email) == None:
        duplicate_mail = False

    # Email Validation
    if not db.verify(email) and is_email(email, check_dns=True):
        try:
            test_msg = yagmail.SMTP(project_address, mailpass)
            test_msg.send(to = email,
                          subject = 'AVS Mail Tester',
                          contents = "Success! Mailing Feature is Functional. " 
                          "If you are not expecting this message, please ignore email.")
            valid_mail = True
        except:
            valid_mail = False
    else:
        valid_mail = False

    #Password Verification
    std_char = re.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,12}$")

    if re.search(std_char, password):
        valid_pass = True
    else:
        valid_pass = False

    # Phone Number Validation
    try:
        if phonenumbers.parse(sms_entry.get()):
            valid_sms = phonenumbers.is_valid_number(phonenumbers.parse(sms_entry.get()))
    except:
            valid_sms = False

    # Error Messages
    if duplicate_mail:
        messagebox.showerror(message="Email Already Registered!")

    elif not valid_mail:
        # Creates Error Window
        messagebox.showerror(message="Invalid Email Address!")

    elif not valid_pass:
        # Creates Error Window
        messagebox.showerror(message='Password must be 8 to 12 characters long and should\n '
                                    'contain at least one (1) digit, uppercase, and lowercase letter.')

    elif not valid_sms:
        # Creates Error Window
        messagebox.showerror(message="Invalid SMS Number!")

    elif not os.path.isdir(directory):
        if is_custom:
          # Creates Error Window
          messagebox.showerror(message="Directory does not Exist!")

        else:
            if not os.path.isdir(directory):
                os.mkdir(directory)

    else:
        disktotal, diskused, diskfree = shutil.disk_usage(directory)
        diskfree = float(diskfree // (2 ** 30))
        diskused = float(diskused // (2 ** 30))
        disktotal = float(disktotal // (2 ** 30))

        if diskfree <= 1:
            messagebox.showerror(message="Not Enough Memory for Disk Space (10% total GB)\nSpace Used: " + str(
                diskused) + " GB Space Used: " + str(diskfree) + " GB")

        else:
            if not os.path.isdir(image_save_path):
                os.mkdir(image_save_path)
            
            password = bytes(password, encoding='utf-8')
            hash = bcrypt.hashpw(password, bcrypt.gensalt(rounds=12))
            #dur = float(delay.perf_counter_ns() - dur)
            #dur = delay.perf_counter_ns()
            #print("\n   Time Elapsed: " + str(dur // 1000000) + " milliseconds")
            #print("\n   Hash Generated: " + str(hash) + "\n")

            db.signup(email, hash, number, directory, image_save_path)
            sms = number + "@sms.clicksend.com"
            capture = camnum.get()
            messagebox.showinfo(title="Success!", message="Successfully Registered!")

            window.destroy()

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Function that recalls the record thread whenever a permitted detection has occurred
def countdown():

    global diskfree, diskused, disktotal

    disktotal, diskused, diskfree = shutil.disk_usage(directory)
    diskfree = float(diskfree // (2 ** 30))
    diskused = float(diskused // (2 ** 30))
    disktotal = float(disktotal // (2 ** 30))

    # Thread initializers
    offset = Thread(target=record)
    offset.daemon = True
    offset.start()

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Performs the 2-sec. offset and recording functions in another thread.
def record():

    global count, istream   # Person counter variable, Stream checking variable
    global notif, permit_record, diskfree, disktotal, pipe
    global buffer_in, frame_out

    hasrecorded = False     # Checks if an image had already been recorded

    delay.sleep(1)          # 1-second offset
    
    if istream:

        start = delay.time()    # Benchmarks with timestamp for the 60-sec. recording

    
        dt = datetime.now()     # Gets exact date and time for naming records
        datestamp = int(dt.strftime("%Y%m%d"))  #Naming (Date)
        timestamp = int(dt.strftime("%H%M%S"))  #Naming (Time)
        
        permit_record = False
        count += 1

        notification.notify(
            title = "DETECTION REPORT",
            message = str(count) + " Detections Made!",
            app_icon = "avs_icon.ico",
            timeout= 20
            )

        if diskfree > 1:
            # Video initialization functions
            video = cv2.VideoWriter(os.path.join(directory, 'VID_' + str(datestamp) + "_" + str(timestamp) + '.avi'),
                            cv2.VideoWriter_fourcc(*'XVID'), 20, (1280, 720))

            # Loop for recording
            while (int(delay.time() - start) < 60) and buffer_in:

                # Frame Fetcher
                ret, image = cap.read()
                video.write(image)

                # Image Snapshot
                if hasrecorded == False:

                    imgname = 'IMG' + str(datestamp) + "_" + str(timestamp) + '.jpg'
                    cv2.imwrite(os.path.join(image_save_path, imgname), image)
                    hasrecorded = True

                    notif = Thread(target=mailer, args=(imgname, dt))
                    notif.daemon = True
                    notif.start()

            # Video Finalizer
            video.release()

        else:
            try:
                # Image Snapshot
                if hasrecorded == False:
                    ret, image = cap.read()
                    imgname = 'IMG' + str(datestamp) + "_" + str(timestamp) + '.jpg'
                    cv2.imwrite(os.path.join(image_save_path, imgname), image)
                    notif = Thread(target=mailer, args=(imgname, dt))
                    notif.daemon = True
                    notif.start()

            except:
                if hasrecorded == False:
                    notif = Thread(target=warning_mailer, args=(dt,))
                    notif.daemon = True
                    notif.start()
    else:
        pipe = True

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Performs Warning Email Notification
def warning_mailer(timestamp):

    global count, sms

    stamp = timestamp.strftime("%B %d, %Y - %I:%M %p") # Timestamp in String
    msg = yagmail.SMTP(project_address, mailpass)

    msg.send(                                           # Mail to User SMS
        to = sms,
        subject = 'auth~pbmallapre@gmail.com~5A31B8F2-A22E-5138-CBC3-F97E63DBB989~ALERT~AVISU',
        contents = "WARNING: Storage Space Insufficient for Recording. Intruder detected on " + stamp
    )
    msg.send(                                           # Mail to User Address
        to = email,
        subject = "Alert!",
        contents = "WARNING: Storage Space Insufficient for Recording. Intruder detected on " + stamp
    )

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Performs Email Notification
def mailer(name, timestamp):

    global count, sms

    stamp = timestamp.strftime("%B %d, %Y - %I:%M %p") # Timestamp in String
    msg = yagmail.SMTP(project_address, mailpass)

    msg.send(                                           # Mail to User SMS
        to = sms,
        subject = 'auth~pbmallapre@gmail.com~5A31B8F2-A22E-5138-CBC3-F97E63DBB989~ALERT~AVISU',
        contents = "Intruder detected on " + stamp
    )
    msg.send(                                           # Mail to User Address
        to = email,
        subject = "Alert!",
        contents = "Intruder detected at " + stamp,
        attachments = os.path.join(image_save_path, name)
    )

#--------------------------------------------------------------------------------------------------------------------------------------------------------------

# Permit and Buffer Functions, Allows for Controlled Detection Stream
def detectbuffer():

    allow = Thread(target=permit)
    allow.daemon = True
    allow.start()

def permit():

    global permit_record, pipe
    delay.sleep(3)
    print("Buffering...")
    permit_record = True
    pipe = True

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Load image helper function
def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# User Input Variables
email = ""
directory = ""
phone_number = ""
image_save_path = ""

# Create Database if it does not already Exist
db = Database('users_log.db')

# Variables for E-mail and Phone
project_address = "avs.detector.notif@gmail.com"
mailpass = "avspy4121"

# Memory-check Variables
disktotal = 0
diskused = 0
diskfree = 0

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# GUI: User Prompt
window = Tk()

cam = [0, 1, 2, 3, 4]

# Window Appearance
window.title("Sign Up: Intruder Detection Application")
window.geometry('335x280')
window.wm_resizable(width='False', height='False')

# Email Widgets
email_label = Label(window, text='Email Address', font=('bold',10), padx=10, pady=10)
email_label.grid(row=0, column=1, sticky=W)
email_entry = Entry(window)
email_entry.grid(row=0, column=2)

password_label = Label(window, text='Password', font=('bold',10), padx=10, pady=10)
password_label.grid(row=1, column=1, sticky=W)
password_label.bind("<Enter>", uncloak)
password_label.bind("<Leave>", cloak)

password_entry = Entry(window, show="*")
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

cam_label = Label(window, text='Camera', font=('bold', 10), padx=10, pady=10)
cam_label.grid(row=4, column=1, sticky=W)

camnum = IntVar(window)
camnum.set(cam[0])

cam_select = OptionMenu(window, camnum, *cam)
cam_select.grid(row=4, column=2, sticky=W)

is_custom = True
custom = Radiobutton(window, text="Save to Public Videos Folder", command=insert, padx=10, pady=10)
custom.grid(row=5, column=1, sticky=W)

# Button
sign_up = Button(window, text='Sign Up', width=12, command=input)
sign_up.grid(row=6, column=2)

login = Button(window, text='Login', width=12, command=switch)
login.grid(row=6, column=1)

window.iconbitmap("avs_icon.ico")
window.mainloop()

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Capture Variables
cap = cv2.VideoCapture(capture)
cap.set(3, 1280)
cap.set(4, 720)

# Set Display for turning off Program
icon = cv2.imread("AVS Show.jpg")

# Stream-check Variables
count = 0
istream = False
permit_record = True

# Variables for E-mail and Phone
project_address = "avs.detector.notif@gmail.com"
mailpass = "avspy4121"

# Video-Buffer Variables
frame_out = delay.time()
buffer_in = True
buffer_out = True
pipe = True

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Path to frozen detection graph and label map.
MODEL_NAME = 'ssdlite_mobilenet_v2_coco_2018_05_09.pb'
PATH_TO_CKPT = os.path.join(os.curdir, 'frozen_models', MODEL_NAME)

LABEL_MAP_NAME = 'label_map.pbtxt'
PATH_TO_LABELS = os.path.join(os.curdir, 'label_maps', LABEL_MAP_NAME)

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Load frozence inference model into memory
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.compat.v1.GraphDef()
    with tf.io.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

# Leave this in case a need to scale or add detections in the future
NUM_CLASSES = 1

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

            cv2.imshow("(Minimize Me) Press Q to Exit", icon)

            # Detection checkers
            if np.count_nonzero(boxes) > 0:

                if not istream and permit_record:
                    print("piping cold")
                    if pipe:
                        print("piping hot")
                        buffer_in = True
                        pipe = False
                        countdown()

                istream = True

            else:
                if istream:
                    print("frame_out is calculated")
                    frame_out = delay.time()
                    istream = False

                if not buffer_out and not permit_record:
                    print("buffer is allowed")
                    detectbuffer()
                    buffer_out = True

                if buffer_in:
                    if (int(delay.time() - frame_out) >= 3):
                        print("buffer is greater than 3")
                        buffer_out = False
                        buffer_in = False

            if cv2.waitKey(25) & 0xFF == ord('q'):
                buffer_in = False
                cv2.destroyAllWindows()
                break

# Background Notification
notification.notify(
            title = "DETECTION REPORT",
            message = str(count) + " Detection(s) Made!",
            app_icon = "avs_icon.ico",
            timeout= 20
            )

# Terminates Main Thread
sys.exit()