# UP FOR DESIGN ADJUSTMENTS AND INTEGRATION TO THE MAIN PROJECT FILE
# STILL NEEDS WIDGETS FOR URL
# WINDOWS FOR EXIT/TERMINATING THE PROGRAM STILL IN PROGRESS

from tkinter import *
from validate_email import validate_email
import socket
import threading as thread

# GUI prompt of the program

ip = ""
email = ""

def validate():
    prompt = thread.Thread(target = input)
    prompt.start()

def withdraw():
    global error
    error.destroy()

def input():

    # User Information
    global ip, email, window, error, sms

    # Creating Error Window
    error = Toplevel()
    error.columnconfigure(0, weight=1)
    error.geometry("200x150")
    error.title("Error")
    error.wm_resizable(width='False', height='False')

    # Fetch User Data
    email = email_entry.get()
    ip = ip_entry.get()
    sms = sms_entry.get()

    # Email Validation
    valid_mail = validate_email(email_address=email, check_format=True, check_blacklist=True, check_dns=True, dns_timeout=10, check_smtp=True, smtp_timeout=10, smtp_helo_host='my.host.name', smtp_from_address='my@from.addr.ess', smtp_debug=False)

    # IP Validation
    try:
        if socket.inet_aton(ip):
            valid_ip = True
    except:
            valid_ip = False

    # SMS Validation
    if len(sms) != 13:
        valid_sms = False
    else:
        valid_sms = True


    if valid_mail and valid_ip and valid_sms:
        window.destroy()
    elif not(valid_mail):
        error_label = Label(error, text='Invalid Email Address!', font=('bold',10), padx=30, pady=10)
        error_label.grid(row=0, column=0, sticky=W)
        ok = Button(error, text='OK', width=12, command=withdraw)
        ok.grid(row=1, column=0)
        error.deiconify()
    elif not(valid_ip):
        error_label = Label(error, text='Invalid IP Address!', font=('bold', 10), padx=30, pady=10)
        error_label.grid(row=0, column=0, sticky=W)
        ok = Button(error, text='OK', width=12, command=withdraw)
        ok.grid(row=1, column=0)
        error.deiconify()
    elif not(valid_sms):
        error_label = Label(error, text='Invalid SMS number!', font=('bold', 10), padx=30, pady=10)
        error_label.grid(row=0, column=0, sticky=W)
        ok = Button(error, text='OK', width=12, command=withdraw)
        ok.grid(row=1, column=0)
        error.deiconify()

# Creates windows
window = Tk()
window.columnconfigure(0, weight=1)

#Window Appearance
window.title("Intruder Detection Application Prompt")
window.geometry('350x300')
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