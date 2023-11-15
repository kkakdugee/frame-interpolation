import os
import shutil
import tempfile
import cv2
from inputs_gui import *

class FrameInterpolation:

    def __init__(self):
        self.temp_folder = tempfile.gettempdir() + "\\interpolation_temp"
        self.create_temp_folder()

    def create_temp_folder(self):
        if not os.path.exists(self.temp_folder):
            os.mkdir(self.temp_folder)

    def get_video(self, input_text="Select Video:"):
        video_directory = get_dir(self.temp_folder, input_text)
        video = cv2.VideoCapture(video_directory)
        return video, video_directory

    def get_video_properties(self, video):
        video_fps = round(float(video.get(cv2.CAP_PROP_FPS)))
        total_frames = round(float(video.get(cv2.CAP_PROP_FRAME_COUNT)))
        length = total_frames / video_fps
        return video_fps, total_frames, length

    def validate_video(self, video_fps, total_frames, length):
        return video_fps > 0 and total_frames > 1 and length > 0

    def process_video(self, video_directory):
        provided_video, video_directory = self.get_video()
        video_fps, total_frames, length = self.get_video_properties(provided_video)

        while not self.validate_video(video_fps, total_frames, length):
            provided_video, video_directory = self.get_video("Invalid Video Provided:")
            video_fps, total_frames, length = self.get_video_properties(provided_video)

        print(f"Video FPS: {video_fps}")
        print(f"Total Frames: {total_frames}")
        print(f"Video Length (s): {length}")

        desired_fps, frames_needed = get_fps(self.temp_folder, video_fps, total_frames, length)

        print(f"Chosen FPS: {desired_fps}")
        print("Frames Needed for Successful Interpolation:", frames_needed)

        frames = load_frames(provided_video, video_fps, total_frames, self.temp_folder)
        print("Successfully Gathered Video Frames")

        frame_pixels = get_pixels(self.temp_folder, frames, total_frames)
        print("Length of Frame Pixels Array:", len(frame_pixels))
        print("Successfully Gathered Frames' Pixels")

        width, height = len(frame_pixels[0][0]), len(frame_pixels[0])
        print("Width of Video:", width)
        print("Height of Video:", height)

        self.cleanup_and_recreate_folder()

        interpolated_frames_pixels = get_new_frames_pixels(self.temp_folder, frame_pixels, total_frames, frames_needed, width, height)
        print("Successfully Gathered Interpolated Frames' Pixels")

        interpolated_frames = get_new_frames(interpolated_frames_pixels, self.temp_folder)
        print("Successfully Created Interpolated Frames")

        new_video(interpolated_frames, video_directory, self.temp_folder, desired_fps)
        print("Successfully Created New Video")

    def cleanup_and_recreate_folder(self):
        shutil.rmtree(self.temp_folder)
        os.mkdir(self.temp_folder)

    def run(self):
        self.process_video()
        self.cleanup_and_recreate_folder()

if __name__ == "__main__":
    interpolator = FrameInterpolator()
    interpolator.run()
