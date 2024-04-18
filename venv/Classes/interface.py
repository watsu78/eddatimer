import threading
import tkinter as tk
import tkinter.font as tkFont
import time
import win32gui
import win32process
import psutil
import json
import constants
import services

# Fonction pour démarrer l'interface utilisateur
def start_interface():
    global counter_label
    global status_value_label
    global directory_label
    global start_button

    font_style = "Arial"

    root = tk.Tk()
    root.title("EDDATIMER")

    #setting window size
    root.geometry('630x500')
    root.resizable(width=False, height=False)

    # Setting the button that is used to chose a map
    directory_button=tk.Button(root,  command=lambda: threading.Thread(target=services.open_directory_dialog()).start())
    directory_button["anchor"] = "center"
    directory_button["bg"] = "#f0f0f0"
    ft = tkFont.Font(family=font_style,size=10)
    directory_button["font"] = ft
    directory_button["fg"] = "#000000"
    directory_button["justify"] = "center"
    directory_button["text"] = "Choose a map"
    directory_button.place(x=20,y=20,width=130,height=50)

    # Setting the map name label
    directory_label=tk.Label(root)
    ft = tkFont.Font(family=font_style,size=15)
    directory_label["font"] = ft
    directory_label["fg"] = "#333333"
    directory_label["justify"] = "center"
    directory_label["text"] = "Select a map before starting"
    directory_label.place(x=160,y=20,width=450,height=50)
    directory_label["borderwidth"] = 1
    directory_label["relief"] = "groove"

    # Setting the start button
    start_button=tk.Button(root,  command=lambda: threading.Thread(target=services.start_counter).start())
    start_button["anchor"] = "center"
    start_button["bg"] = "#f0f0f0"
    ft = tkFont.Font(family=font_style,size=18)
    start_button["font"] = ft
    start_button["fg"] = "#000000"
    start_button["justify"] = "center"
    start_button["text"] = "START"
    start_button.place(x=80,y=300,width=460,height=76)
    start_button["state"] = "disable"

    # Setting the stop button
    stop_button = tk.Button(root, command=lambda: threading.Thread(target=services.stop_counter()).start())
    stop_button["bg"] = "#f0f0f0"
    ft = tkFont.Font(family=font_style,size=18)
    stop_button["font"] = ft
    stop_button["fg"] = "#000000"
    stop_button["justify"] = "center"
    stop_button["text"] = "STOP"
    stop_button.place(x=200,y=390,width=224,height=82)

    # Setting the Counter label
    counter_label=tk.Label(root)
    ft = tkFont.Font(family=font_style,size=48)
    counter_label["font"] = ft
    counter_label["fg"] = "#333333"
    counter_label["bg"] = "#ffe6e6"
    counter_label["justify"] = "center"
    counter_label["text"] = ""
    counter_label.place(x=30,y=100,width=569,height=134)
    counter_label["borderwidth"] = 1
    counter_label["relief"] = "solid"

    status_title_label=tk.Label(root)
    ft = tkFont.Font(family=font_style,size=10)
    status_title_label["font"] = ft
    status_title_label["fg"] = "#333333"
    status_title_label["justify"] = "center"
    status_title_label["text"] = "Tracking status"
    status_title_label.place(x=450,y=470,width=90,height=25)

    status_value_label=tk.Label(root)
    ft = tkFont.Font(family=font_style,size=10)
    status_value_label["font"] = ft
    status_value_label["fg"] = "#333333"
    status_value_label["bg"] = "#ff5722"
    status_value_label["justify"] = "center"
    status_value_label["text"] = constants.status_stopped
    status_value_label.place(x=545,y=470,width=80,height=25)


    root.mainloop()

def update_state_start_button(state):
    start_button.config(state=state)

def update_counter_label(total_elapsed_time):

    hours = int(total_elapsed_time) // 3600
    minutes = (int(total_elapsed_time) % 3600) // 60
    seconds = int(total_elapsed_time) % 60

    time_str = f"{hours}:{str(minutes).zfill(2)}:{str(seconds).zfill(2)}"

    counter_label.config(text=time_str)

def update_status_value(text):
    status_value_label.config(text=text)

    match text:
        case constants.status_active:
            status_value_label.config(bg="#5fb878")
        case constants.status_inactive:
            status_value_label.config(bg="#01aaed")
        case _:
            status_value_label.config(bg="#ff5722")

def update_directory_label(text):

    match text:
        case "ERROR_INCORRECT_DIRECTORY":
            directory_label.config(fg="red")
            directory_label.config(text="The selected folder is not a map folder")
            start_button.config(state="disable")
        case _:
            directory_label.config(fg="black")
            directory_label.config(text=text)
            start_button.config(state="normal")