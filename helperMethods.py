from moviepy.editor import *


def validFile(provided_path):
    from pymediainfo import MediaInfo

    media_info = ""

    try:
        media_info = MediaInfo.parse(provided_path)
    except FileNotFoundError:
        return False
    
    for track in media_info.tracks:
        if track.track_type == "Video":
            return True

def get_frames(video, temp_folder, window):
    import cv2

    frames = []

    frame = 0
    success, image = video.read()

    while success: 
        frame += 1
        window.write_event_value("-UP-", frame)

        img_path = rf"{temp_folder}\Frame {frame}.jpg".format(temp_folder, frame)
        cv2.imwrite(img_path, image)
        frames.append(img_path)
        
        success, image = video.read()

    window.write_event_value("Exit", frames)

def get_possible_fps(total_frames, length):

    fps_list = {}

    frames_added = total_frames - 1
    total_frames += frames_added
    frames_added *= 2

    while total_frames / length + 2.4 <= 242.5: # 1% margin of error
        new_fps = round(total_frames / length)
        fps_list[new_fps] = total_frames
        total_frames += frames_added
        frames_added *= 2

    return fps_list

def get_buttons(possible_fps):
    import PySimpleGUI as sg

    button_list = []

    for fps in possible_fps:
        button_list.append(sg.Button(str(fps)))
    
    return button_list

def all_pixels(frames, window):

    import cv2
    import numpy

    frame_pixels = []
    count = 1

    for frame in frames:
        frame_pixels.append(cv2.imread(frame))
        window.write_event_value("-UP-", count)
        count += 1

    window.write_event_value("Exit", frame_pixels)

def get_interpolated(frame_pixels, total_frames, width, height, window):

    import cv2
    import numpy as np

    count = 1

    while len(frame_pixels) != total_frames:

        interpolated_frames = []

        current_length = len(frame_pixels)

        for i in range(1, current_length):

            frame_one = frame_pixels[i - 1]
            frame_two = frame_pixels[i]
            new_frame = np.full((height, width, 3), 255, dtype = np.uint8)

            for j in range(height):
                for k in range(width):

                    pixel_one = frame_one[j][k]
                    pixel_two = frame_two[j][k]
                    new_pixel = interpolate(pixel_one, pixel_two)
                    new_frame[j, k] = new_pixel
                    #print(f"Pixel One: {pixel_one} Pixel Two: {pixel_two}, New Pixel: {new_pixel}".format(pixel_one, pixel_two, new_pixel))

            interpolated_frames.append(new_frame)
            window.write_event_value("-UP-", count)

            count += 1

        i = 1 # all frames index
        j = 0 # just interpolated frames index
        combined_length = current_length + len(interpolated_frames)
        while i < combined_length and j < len(interpolated_frames):
            frame_pixels.insert(i, interpolated_frames[j])
            i += 2
            j += 1

        
    window.write_event_value("Exit", frame_pixels)


def interpolate(pixel_one, pixel_two):
    red = round((int(pixel_one[2]) + int(pixel_two[2])) / 2)
    green = round((int(pixel_two[1]) + int(pixel_two[1])) / 2)
    blue = round((int(pixel_one[0]) + int(pixel_two[0])) / 2)
    return [blue, green, red]

def create_new_frames(interpolated_frame_pixels, temp_folder, window):

    import cv2
    import numpy

    new_frames_dir = []

    count = 1

    for frame in interpolated_frame_pixels:

        img_path = rf"{temp_folder}\\Frame {count}.jpg".format(temp_folder, count)

        cv2.imwrite(img_path, frame)

        new_frames_dir.append(img_path)

        window.write_event_value("-UP-", count)

        count += 1

    window.write_event_value("Exit", new_frames_dir)


def create_video(frames, video_directory, temp_folder, desired_fps, window):
    import cv2
    window.write_event_value("-UP-", 1)

    original_video = VideoFileClip(video_directory)
    audio = original_video.audio

    audio.write_audiofile("audio.mp3")


    window.write_event_value("-UP-", 2)

    images = []

    for frame in frames:
        image = ImageClip(frame, duration = (1 / desired_fps))
        images.append(image)

    video_images = concatenate_videoclips(images, method = "compose")
    video_images.write_videofile("test.mp4", desired_fps)

    window.write_event_value("-UP-", 3)

    new_video = VideoFileClip("test.mp4")
    audio = AudioFileClip("audio.mp3")

    new_audio = CompositeAudioClip([audio])
    new_video.audio = new_audio
    new_video.write_videofile("final.mp4")

    window.write_event_value("Exit", "")




def delete_temp(temp_folder):
    import shutil
    shutil.rmtree(temp_folder)
