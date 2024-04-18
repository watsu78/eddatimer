import sys
import threading
import tkinter as tk
import time
import win32gui
import win32process
import psutil
import json
import constants
import interface
import tkinter.font as tkFont
from tkinter import filedialog
import os
import queue

# Initialize a queue
stop_queue = queue.Queue()

# flag to indicate if the tracking is active
is_tracking = False

# Begining time of the tracking
start_time = None

# Name of the currently tracked map
current_song_name = None

# get the PID of EDDA
def get_pid_by_name(process_name):
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == process_name:
            return process.info['pid']
    return None

# get the title of the active window
def get_active_window_title():
    return win32gui.GetWindowText(win32gui.GetForegroundWindow())

# Check if a window belongs to a specific process
def is_window_from_process(window_handle, process_id):
    window_process_id = win32process.GetWindowThreadProcessId(window_handle)[1]
    return window_process_id == process_id

# Load the time from the JSON file depending on the map name
def load_total_time(json_file_path):
    global current_song_name

    if current_song_name:
        try:
            with open(json_file_path, "r") as file:
                data = json.load(file)
            if current_song_name in data:
                return data[current_song_name]["total_time"]
            else:
                return 0
        except FileNotFoundError:
            return 0
    else:
        return 0

# Save the spent time on a JSON file
def save_total_time(json_file_path, total_time):
    global current_song_name

    try:
        with open(json_file_path,'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}

    # Assurez-vous que current_song_name est défini
    if current_song_name:
        # Ajoutez ou mettez à jour la valeur total_time associée à current_song_name
        if current_song_name in data:
            data[current_song_name]["total_time"] = total_time
        else:
            data[current_song_name] = {"total_time": total_time}

    with open(json_file_path,'w') as file:
        json.dump(data,file)


# Fonction pour logger les messages
def write_log(message):
    with open(constants.log_file_path, "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - "+ message +"\n")
        log_file.flush()

# Fonction pour démarrer le compteur
def start_counter():
    global is_tracking
    global start_time
    global total_elapsed_time
    global target_process_pid

    target_process_pid = get_pid_by_name(constants.target_process_title)
    try:
        while not target_process_pid:
            target_process_pid = get_pid_by_name(constants.target_process_title)
            #write_log("tentative de recuperation du PID de EDDA")
    except KeyboardInterrupt:
        print("huho bye bye")
        #write_log("Echec de la recuperation du PID de Edda")


    #write_log(f"Recuperation du PID de Edda : {target_process_pid}")

    is_stopped = True
    is_tracking = True
    interface.update_status_value(constants.status_active)
    interface.update_state_start_button("disabled")
    start_time = time.time()
    total_elapsed_time = load_total_time(constants.json_file_path)
    update_counter(target_process_pid, constants.target_window_title, constants.json_file_path)

# Fonction pour mettre à jour le compteur en temps réel
def update_counter(target_process_pid, target_window_title, json_file_path):
    #write_log("Début du tracking")
    global is_tracking
    global start_time
    global total_elapsed_time
    global is_stopped

    try:
        while True:
            current_window_title = get_active_window_title()
            current_window_handle = win32gui.GetForegroundWindow()

            if current_window_title == constants.target_window_title and is_window_from_process(current_window_handle, target_process_pid):
                if not is_tracking:
                    total_elapsed_time = load_total_time(json_file_path)
                    is_tracking = True
                    interface.update_status_value(constants.status_active)
                    #write_log("Recuperation du focus - reprise du tracking")
                else:
                    elapsed_time = time.time() - start_time
                    total_elapsed_time += elapsed_time

                interface.update_counter_label(total_elapsed_time)

                start_time = time.time()  # Réinitialiser le temps de départ
            else:
                #write_log("Perte du focus, mise en veille")
                is_tracking = False
                interface.update_status_value(constants.status_inactive)
                save_total_time(json_file_path, total_elapsed_time)

                interface.update_counter_label(total_elapsed_time)

            # Vérifiez si un message d'arrêt a été reçu
            try:
                stop_signal = stop_queue.get_nowait()
                if stop_signal:
                    #write_log("Arret du tracking")
                    save_total_time(json_file_path, total_elapsed_time)
                    interface.update_counter_label(total_elapsed_time)
                    interface.update_status_value(constants.status_stopped)
                    interface.update_state_start_button("normal")
                break  # Quittez la boucle si un message d'arrêt a été reçu
            except queue.Empty:
                pass  # Gérez le cas où la queue est vide

            time.sleep(1)  # Attendez une seconde avant de vérifier à nouveau
    except KeyboardInterrupt:
        print("Good Bye")

def reset_counter():
    data = {"total_time": 0}
    with open(constants.json_file_path, "w") as file:
        json.dump(data, file)
    #write_log("Reset du compteur de temps")

def stop_counter():
    try:
        # Envoyez un message à la queue indiquant d'arrêter la boucle
        stop_queue.put(True)
    except queue.Full:
        pass  # Gérez le cas où la queue est pleine

def open_directory_dialog():
    selected_directory = filedialog.askdirectory()
    infodatfile = os.path.join(selected_directory, "info.dat")
    global current_song_name

    try:
        with open(infodatfile, "r") as file:
            data = json.load(file)
            current_song_name = data["_songName"]
        # Faites quelque chose avec le dossier sélectionné, par exemple, l'afficher dans un label
        if current_song_name:
            #write_log(f"map sélectionnée : {current_song_name}")

            # Mettez à jour l'interface utilisateur avec le chemin du dossier sélectionné
            interface.update_directory_label(current_song_name)

    except FileNotFoundError:
        interface.update_directory_label("ERROR_INCORRECT_DIRECTORY")

