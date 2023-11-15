import sys
import threading
import PySimpleGUI as sg
from helper import *

class FrameInterpolationGUI:
    
    SIZE = (600, 150)
    TITLE = "Frame Interpolation"

    def __init__(self, temp_folder):
        self.temp_folder = temp_folder

    def get_dir(self, input_text="Select a video:"):
        layout = [[sg.Text(input_text), sg.Input(key="-IN-"), sg.FileBrowse(key="-IN-")],
                  [sg.Button("Submit")]]
        return self._create_window(layout, self._handle_get_dir)

    def get_fps(self, video_fps, total_frames, length):
        possible_fps_dict = get_possible_fps(total_frames, length)
        possible_fps = [fps for fps in possible_fps_dict]
        print("Possible FPS:", possible_fps)
        button_list = get_buttons(possible_fps)
        layout = [[sg.Text("Enter Desired FPS (Frames Per Second):")], [button_list]]
        return self._create_window(layout, self._handle_get_fps, possible_fps_dict)

    def load_frames(self, video, video_fps, total_frames):
        layout = self._progress_bar_layout("Gathering Video Frames:", total_frames)
        return self._create_window(layout, self._handle_load_frames, video, video_fps, total_frames)

    # Other methods like get_pixels, get_new_frames_pixels, get_new_frames, new_video

    def _create_window(self, layout, handler, *args):
        window = sg.Window(self.TITLE, layout, size=self.SIZE, finalize=True)
        return handler(window, *args)

    def _progress_bar_layout(self, text, max_value):
        return [[sg.Text(text)],
                [sg.ProgressBar(max_value=max_value, orientation="h", size=(75, 20), key="-PROG-")],
                [sg.StatusBar(text="", size=(25, 25), key="-PROG2-")]]

    def _handle_get_dir(self, window):
        # Event handling logic for get_dir
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED:
                self._exit(window)
            elif event == "Submit":
                provided_path = values["-IN-"]
                if validFile(provided_path):
                    window.close()
                    return provided_path
                else:
                    sg.popup("Invalid File Type. Select a video:")

    def _handle_get_fps(self, window, possible_fps_dict):
        # Event handling logic for get_fps
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED:
                self._exit(window)
            if event in possible_fps_dict:
                window.close()
                return (event, possible_fps_dict[event])

    def _handle_load_frames(self, window, video, video_fps, total_frames):
        # Event handling logic for load_frames
        threading.Thread(target=get_frames, args=(video, self.temp_folder, lambda frame: window.write_event_value("-UP-", frame)), daemon=True).start()
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED:
                self._exit(window)
            elif event == "-UP-":
                frame = values[event]
                update_text = f"Frame {frame} / {total_frames}"
                window["-PROG-"].update(frame)
                window["-PROG2-"].update(update_text)
            elif event == "Exit":
                window.close()
                return values[event]

    # Other handler methods

    def _exit(self, window):
        delete_temp(self.temp_folder)
        window.close()
        sys.exit()

if __name__ == "__main__":
    gui = FrameInterpolationGUI(temp_folder="path_to_temp_folder")
    # Example usage
    video_path = gui.get_dir()
