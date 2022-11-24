import os
import shutil
import tempfile

import cv2

from inputsGUI import *


def main():

    temp_folder = tempfile.gettempdir() + "\\interpolation_temp"

    os.mkdir(temp_folder)

    # path file of the provided video
    video_directory = get_dir(temp_folder)

    # get the video
    provided_video = cv2.VideoCapture(video_directory)

    # calculate the fps, total frame count, & length (in seconds) of the provided video
    video_fps = round(float(provided_video.get(cv2.CAP_PROP_FPS)))
    total_frames = round(float(provided_video.get(cv2.CAP_PROP_FRAME_COUNT)))
    length = total_frames / video_fps

    while video_fps <= 0 or total_frames <= 1 or length <= 0:
        video_directory = get_dir(input_text = "Invalid Video Provided:")
        provided_video = cv2.VideoCapture(video_directory)
        video_fps = round(float(provided_video.get(cv2.CAP_PROP_FPS)))
        total_frames = round(float(provided_video.get(cv2.CAP_PROP_FRAME_COUNT)))
        length = total_frames / video_fps

    print(f"Video FPS: {video_fps}".format(video_fps))
    print(f"Total Frames: {total_frames}".format(total_frames))
    print(f"Video Length (s): {length}".format(length))

    temp = get_fps(temp_folder, video_fps, total_frames, length)

    # obtain the desired fps
    desired_fps = temp[0]

    print(f"Chosen FPS: {desired_fps}".format(desired_fps))

    # obtain the total amount of frames required
    frames_needed = temp[1]

    print("Frames Needed for Successful Interpolation:", frames_needed)

    # extract the frames of the provided video
    frames = load_frames(provided_video, video_fps, total_frames, temp_folder)

    print("Successfully Gathered Video Frames")

    # gather the pixels of each frame and store them into a list
    frame_pixels = get_pixels(temp_folder, frames, total_frames)

    print("Length of Frame Pixels Array:", len(frame_pixels))

    print("Successfully Gathered Frames' Pixels")

    width = len(frame_pixels[0][0])
    height = len(frame_pixels[0])

    print("Width of Video:", width)
    print("Height of Video:", height)

    shutil.rmtree(temp_folder)
    os.mkdir(temp_folder)

    interpolated_frames_pixels = get_new_frames_pixels(temp_folder, frame_pixels, total_frames, frames_needed, width, height)

    print("Successfully Gathered Interpolated Frames' Pixels")

    interpolated_frames = get_new_frames(interpolated_frames_pixels, temp_folder)

    print("Successfully Created Interpolated Frames")


    new_video(interpolated_frames, video_directory, temp_folder, desired_fps)

    print("Successfully Created New Video")

    shutil.rmtree(temp_folder)



if __name__ == "__main__":
    main()
