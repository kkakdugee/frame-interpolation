import sys
import threading

import cv2
import PySimpleGUI as sg

from helperMethods import *

SIZE = (600, 150)
TITLE = "Frame Interpolation"

def get_dir(temp_folder, input_text = "Select a video:"):

    layout = [  [sg.Text(input_text), sg.Input(key = "-IN-", change_submits = True), sg.FileBrowse(key = "-IN-")],
                [sg.Button("Submit")]]

    window = sg.Window(TITLE, layout, size = SIZE)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            delete_temp(temp_folder)
            sys.exit()
        elif event == "Submit":
            window.close()
            provided_path = values["-IN-"]
            if validFile(provided_path):
                return provided_path
            else:
                return get_dir(input_text = "Invalid File Type. Select a video:")


def get_fps(temp_folder, video_fps, total_frames, length):

    possible_fps_dict = get_possible_fps(total_frames, length)
    possible_fps = [fps for fps in possible_fps_dict]

    print("Possible FPS:", possible_fps)

    button_list = get_buttons(possible_fps)

    layout = [ [sg.Text("Enter Desired FPS (Frames Per Second):")], [button_list] ]
    
    # layout.append(button_list)

    window = sg.Window(TITLE, layout, size = SIZE)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            delete_temp(temp_folder)
            sys.exit()
        for fps in possible_fps:
            if event == str(fps):
                window.close()
                return (fps, possible_fps_dict[fps])

def load_frames(video, video_fps, total_frames, temp_folder):
    
    layout = [  [sg.Text("Gathering Video Frames:")],
                [sg.ProgressBar(max_value = total_frames, orientation = "h", size = (75, 20), key = "-PROG-")],
                [sg.StatusBar(text = "", size = (25, 25), key = "-PROG2-")]]

    main_window = sg.Window(TITLE, layout, size = SIZE, finalize = True)

    main_window["-PROG-"].update(1)

    threading.Thread(target = get_frames, args = (video, temp_folder, main_window), daemon = True).start()

    while True:
        window, event, values = sg.read_all_windows()
        if event == sg.WIN_CLOSED:
            delete_temp(temp_folder)
            sys.exit()
        elif event == "Exit":
            break
        elif event == "-UP-":
            frame = values[event]
            update_text = f"Frame {frame} / {total_frames}".format(frame, total_frames)

            window["-PROG-"].update(frame)
            window["-PROG2-"].update(update_text)

            window.refresh()
    window.close()
    return values[event]


def get_pixels(temp_folder, frames, total_frames):

    layout = [  [sg.Text("Gathering Frames' Pixels:")],
                [sg.ProgressBar(max_value = total_frames, orientation = "h", size = (75, 20), key = "-PROG-")],
                [sg.StatusBar(text = "", size = (25, 25), key = "-PROG2-")]]

    main_window = sg.Window(TITLE, layout, size = SIZE, finalize = True)

    main_window["-PROG-"].update(1)

    threading.Thread(target = all_pixels, args = (frames, main_window), daemon = True).start()

    while True:
        window, event, values = sg.read_all_windows()
        if event == sg.WIN_CLOSED:
            delete_temp(temp_folder)
            sys.exit()
        elif event == "Exit":
            break    
        elif event == "-UP-":
            frame = values[event]
            update_text = f"Frame {frame} / {total_frames}".format(frame, total_frames)

            window["-PROG-"].update(frame)
            window["-PROG2-"].update(update_text)

            window.refresh()
    window.close()
    return values[event]


def get_new_frames_pixels(temp_folder, frame_pixels, total_frames, frames_needed, width, height):

    total_frames = frames_needed - total_frames

    layout = [  [sg.Text("Calculating Interpolated Frames:")],
                [sg.ProgressBar(max_value = total_frames, orientation = "h", size = (75, 20), key = "-PROG-")],
                [sg.StatusBar(text = "", size = (25, 25), key = "-PROG2-")]]

    main_window = sg.Window(TITLE, layout, size = SIZE, finalize = True)

    main_window["-PROG-"].update(0)

    threading.Thread(target = get_interpolated, args = (frame_pixels, frames_needed, width, height, main_window), daemon = True).start()

    while True:
        window, event, values = sg.read_all_windows()
        if event == sg.WIN_CLOSED:
            delete_temp(temp_folder)
            sys.exit()
        elif event == "Exit":
            break    
        elif event == "-UP-":
            frame = values[event]
            update_text = f"Frame {frame} / {total_frames}".format(frame, total_frames)

            window["-PROG-"].update(frame)
            window["-PROG2-"].update(update_text)

            window.refresh()
    window.close()
    return values[event]

def get_new_frames(interpolated_frame_pixels, temp_folder):

    total_frames = len(interpolated_frame_pixels)

    layout = [  [sg.Text("Creating Interpolated Frames:")],
                [sg.ProgressBar(max_value = total_frames, orientation = "h", size = (75, 20), key = "-PROG-")],
                [sg.StatusBar(text = "", size = (25, 25), key = "-PROG2-")]]

    main_window = sg.Window(TITLE, layout, size = SIZE, finalize = True)

    main_window["-PROG-"].update(1)

    threading.Thread(target = create_new_frames, args = (interpolated_frame_pixels, temp_folder, main_window), daemon = True).start()


    while True:
        window, event, values = sg.read_all_windows()
        if event == sg.WIN_CLOSED:
            delete_temp(temp_folder)
            sys.exit()
        elif event == "Exit":
            break    
        elif event == "-UP-":
            frame = values[event]
            update_text = f"Frame {frame} / {total_frames}".format(frame, total_frames)

            window["-PROG-"].update(frame)
            window["-PROG2-"].update(update_text)

            window.refresh()
    window.close()
    return values[event]


def new_video(frames, video, temp_folder, desired_fps):

    layout = [  [sg.Text("Creating Video:")],
                [sg.StatusBar(text = "", size = (25, 25), key = "-PROG-")]]

    main_window = sg.Window(TITLE, layout, size = SIZE, finalize = True)

    threading.Thread(target = create_video, args = (frames, video, temp_folder, desired_fps, main_window), daemon = True).start()


    while True:
        window, event, values = sg.read_all_windows()
        if event == sg.WIN_CLOSED:
            delete_temp(temp_folder)
            sys.exit()
        elif event == "Exit":
            break    
        elif event == "-UP-":
            status = values[event]
            update_text = ""
            if status == 1:
                update_text = "Extracting Audio..."
            elif status == 2:
                update_text = "Combining New Frames..."
            elif status == 3:
                update_text = "Combining Audio and New Video..."
            window["-PROG-"].update(update_text)
            window.refresh()
    window["-PROG-"].update("Done!")
