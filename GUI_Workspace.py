import sys
import os, re
import threading as thread

# User Prompt imports
import socket
import phonenumbers                         # Needs Installation
from tkinter import *
from tkinter import messagebox
from validate_email import validate_email   # Needs Installation

# E-mail import
import yagmail                              # Needs Installation

from pathlib import Path

from user_db import Database

db = Database('users_log.db')

def validate():
    # Validates within another Thread
    global prompt
    prompt = thread.Thread(target = input)
    prompt.daemon = True
    prompt.start()

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

    global email, ip, sms, directory
    user_info = db.login(user_entry.get(), pass_entry.get())

    if user_info == None:
        messagebox.showerror(title="Invalid input!", message="No User Found.")

    else:
        messagebox.showinfo(message="Login Successful!")
        email = user_info[1]
        ip = user_info[3]
        sms = user_info[4]
        directory = user_info[5]
        print(email+" "+ip+" "+sms+" "+directory)
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
    global ip, email, window, error, sms, phone_number, is_custom
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
    password = password_entry.get()
    directory = vid_entry.get()
    number = sms_entry.get()


    # Email Validation
    valid_mail = validate_email(email_address=email, check_format=True, check_blacklist=True, check_dns=True,
                                dns_timeout=10, check_smtp=True, smtp_timeout=10, smtp_helo_host='my.host.name',
                                smtp_from_address='my@from.addr.ess', smtp_debug=False)

    #Password Verification
    special_char = re.compile("^(?=.*[a-z])(?=.*\d)[A-Za-z\d]{8,20}$")
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

    # IP Validation
    try:
        if socket.inet_aton(ip):
            valid_ip = True
    except:
            valid_ip = False


    # Error Messages
    if not db.verify(email) == None:

        messagebox.showerror(message="Email Already Registered!")

    elif not os.path.isdir(directory):

        if is_custom:

          wait.destroy()

          # Creates Error Window
          messagebox.showerror(message="Directory does not Exist!")

        else:
            os.mkdir(vid_entry.get())

    elif not valid_mail:

        wait.destroy()

        # Creates Error Window
        messagebox.showerror(message="Invalid Email Address!")

    elif not valid_pass:

        wait.destroy()

        # Creates Error Window
        messagebox.showerror(message='Password must be 8 to 20 characters long and should\n '
                                        'only contain at least one (1) digit and both letter cases!')

    elif not valid_ip:

        wait.destroy()

        # Creates Error Window
        messagebox.showerror(message="Invalid IP Address!")

    elif not valid_sms:

        wait.destroy()

        # Creates Error Window
        messagebox.showerror(message="Invalid SMS Number!")

    else:
        db.signup(email, password, ip, number, directory)
        phone_number = sms_entry.get() + "@sms.clicksend.com"
        try:
            log.destroy()
        except:
            wait.destroy()
            window.destroy()
        wait.destroy()
        window.destroy()

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# GUI: User Prompt
window = Tk()

# Window Appearance
window.title("Sign Up: Intruder Detection Application")
window.geometry('340x300')
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

# IP Widgets
ip_label = Label(window, text='IP Address', font=('bold',10), padx= 10, pady=10)
ip_label.grid(row=2, column=1, sticky=W)
ip_entry = Entry(window)
ip_entry.grid(row=2, column=2)

# SMS Widgets
country_code = StringVar()
sms_label = Label(window, text='Phone Number', font=('bold',10), padx= 10, pady=10)
sms_label.grid(row=3, column=1, sticky=W)
sms_entry = Entry(window, textvariable = country_code)
sms_entry.insert(0, "+63")
sms_entry.grid(row=3, column=2)

vid_dir = Label(window, text='Video Directory', font=('bold', 10), padx=10, pady=10)
vid_dir.grid(row=4, column=1, sticky=W)
vid_entry = Entry(window)
vid_entry.grid(row=4, column=2)

is_custom = True
custom = Radiobutton(window, text="Save to Public Videos Folder", command=disable, padx=10, pady=10)
custom.grid(row=5, column=1, sticky=W)

# Button
sign_up = Button(window, text='Sign Up', width=12, command=validate)
sign_up.grid(row=6, column=2)

login = Button(window, text='Login', width=12, command=switch)
login.grid(row=6, column=1)

window.mainloop()

sys.exit()