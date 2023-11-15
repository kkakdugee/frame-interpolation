import os
from video_generation_pipeline import main
import frame_extraction_and_preprocessing

def get_user_choice():
    while True:
        try:
            choice = int(input("Generate Video (1) or Preprocess (2): "))
            if choice in [1, 2]:
                return choice
            else:
                print("Invalid input. Please enter 1 to generate a video or 2 to preprocess.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

def get_video_name():
    while True:
        video_name = input("Input Video Name (with extension): ")
        if os.path.isfile(os.path.join(frame_extraction_and_preprocessing.VIDEO_DIR, video_name)):
            return video_name
        else:
            print("Invalid video name or file not found. Please try again.")

def get_multiplier():
    while True:
        try:
            multiplier = int(input("Enter the interpolation multiplier (1, 2, 3, ...): "))
            if multiplier >= 1:
                return multiplier
            else:
                print("Invalid input. The multiplier must be 1 or greater.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

which = get_user_choice()

if which == 1:
    video_name = get_video_name()
    video_folder = os.path.splitext(video_name)[0]
    video_fps = frame_extraction_and_preprocessing.gather_frames(video_name, video_folder)
    multiplier = get_multiplier()
    main(multiplier, video_name, video_folder, video_fps)
elif which == 2:
    frame_extraction_and_preprocessing.preprocess_frames()
