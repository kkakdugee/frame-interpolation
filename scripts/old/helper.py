import cv2
import numpy as np
import shutil
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, ImageClip
from pymediainfo import MediaInfo

def is_valid_file(file_path):
    try:
        media_info = MediaInfo.parse(file_path)
        return any(track.track_type == "Video" for track in media_info.tracks)
    except FileNotFoundError:
        return False

def extract_frames(video, temp_folder, update_callback):
    frame_count = 0
    success, image = video.read()
    frames = []

    while success:
        frame_count += 1
        update_callback(frame_count)
        img_path = f"{temp_folder}/Frame {frame_count}.jpg"
        cv2.imwrite(img_path, image)
        frames.append(img_path)
        success, image = video.read()

    update_callback("Exit", frames)

def calculate_possible_fps(total_frames, length):
    fps_options = {}
    frames_added = total_frames - 1

    while (total_frames + frames_added) / length <= 242.5:  # 1% margin of error
        new_fps = round((total_frames + frames_added) / length)
        fps_options[new_fps] = total_frames + frames_added
        frames_added *= 2

    return fps_options

def extract_pixels_from_frames(frames, update_callback):
    frame_pixels = []
    for count, frame_path in enumerate(frames, start=1):
        frame_pixels.append(cv2.imread(frame_path))
        update_callback(count)

    update_callback("Exit", frame_pixels)

def interpolate_frames(frame_pixels, total_frames, update_callback):
    while len(frame_pixels) < total_frames:
        interpolated_frames = []

        for i in range(1, len(frame_pixels)):
            new_frame = interpolate_two_frames(frame_pixels[i - 1], frame_pixels[i])
            interpolated_frames.append(new_frame)
            update_callback(len(interpolated_frames))

        frame_pixels = interleave_frames(frame_pixels, interpolated_frames)

    update_callback("Exit", frame_pixels)

def interpolate_two_frames(frame_one, frame_two):
    height, width = frame_one.shape[:2]
    new_frame = np.full((height, width, 3), 255, dtype=np.uint8)

    for j in range(height):
        for k in range(width):
            new_frame[j, k] = interpolate_pixels(frame_one[j, k], frame_two[j, k])

    return new_frame

def interpolate_pixels(pixel_one, pixel_two):
    return [
        round((pixel_one[0] + pixel_two[0]) / 2),
        round((pixel_one[1] + pixel_two[1]) / 2),
        round((pixel_one[2] + pixel_two[2]) / 2)
    ]

def interleave_frames(original_frames, new_frames):
    result = []
    for original, new in zip(original_frames, new_frames):
        result.extend([original, new])
    result.append(original_frames[-1])
    return result

def create_frames_from_pixels(interpolated_pixels, temp_folder, update_callback):
    new_frames = []

    for count, pixels in enumerate(interpolated_pixels, start=1):
        img_path = f"{temp_folder}/Frame {count}.jpg"
        cv2.imwrite(img_path, pixels)
        new_frames.append(img_path)
        update_callback(count)

    update_callback("Exit", new_frames)

def create_video_with_audio(frames, video_directory, desired_fps, update_callback):
    original_video = VideoFileClip(video_directory)
    audio = original_video.audio
    audio.write_audiofile("audio.mp3")
    update_callback(1)

    clips = [ImageClip(frame, duration=(1 / desired_fps)) for frame in frames]
    video_clip = concatenate_videoclips(clips, method="compose")
    video_clip.write_videofile("test.mp4", fps=desired_fps)
    update_callback(2)

    final_video = VideoFileClip("test.mp4").set_audio(AudioFileClip("audio.mp3"))
    final_video.write_videofile("final.mp4")
    update_callback(3)

def delete_temp_folder(temp_folder):
    shutil.rmtree(temp_folder)
