import os
import cv2
import numpy as np

# Define the directories for raw and processed frames
RAW_DATA_DIR = "./data/raw_frames"
PROCESSED_DATA_DIR = "./data/processed_frames"
VIDEO_DIR = './videos'

def gather_frames(video_name, video_folder):
    """
    Reads a video file frame by frame and saves each frame as an image.

    Args:
    - video_name (str): The filename of the video to process.
    """

    # Open the video file
    video_path = os.path.join(VIDEO_DIR, video_name)
    video = cv2.VideoCapture(video_path)

    success, image = video.read()
    frame_count = 0

    raw_video_dir = os.path.join(RAW_DATA_DIR, video_folder)

    os.makedirs(raw_video_dir, exist_ok=True)

    # Loop through each frame in the video
    while success:
        frame_count += 1
        img_path = os.path.join(raw_video_dir, f"Frame_{frame_count}.png")
        # Save the current frame as an image file
        cv2.imwrite(img_path, image)
        success, image = video.read()  # Read the next frame

    video_fps = round(video.get(cv2.CAP_PROP_FPS))
    
    video.release()

    return video_fps

def preprocess_frames(target_size=(1280, 720)):
    """
    Preprocesses all frames by resizing and normalizing them, then saves as .npy files.

    Args:
    - target_size (tuple): The desired size (width, height) for the processed frames.
    """

    # Process each video folder in the raw data directory
    for video_folder in os.listdir(RAW_DATA_DIR):
        print(f"Preprocessing {video_folder}")

        # Construct paths for the raw and processed video frames
        raw_video_path = os.path.join(RAW_DATA_DIR, video_folder)
        processed_video_path = os.path.join(PROCESSED_DATA_DIR, video_folder)

        # Create the directory for processed frames if it does not exist
        if not os.path.exists(processed_video_path):
            os.makedirs(processed_video_path)

        # Loop through each frame image file
        for frame_file in sorted(os.listdir(raw_video_path)):
            raw_frame_path = os.path.join(raw_video_path, frame_file)
            
            # Construct the filename for the processed frame
            processed_frame_filename = os.path.splitext(frame_file)[0] + '.npy'
            processed_frame_path = os.path.join(processed_video_path, processed_frame_filename)

            # Read the frame image file
            frame = cv2.imread(raw_frame_path)
            if frame is None:
                print(f"Warning: Could not read {raw_frame_path}")
                continue

            # Resize the frame and normalize pixel values
            resized_frame = cv2.resize(frame, target_size)
            normalized_frame = resized_frame / 255.0
            # Save the preprocessed frame as a .npy file
            np.save(processed_frame_path, normalized_frame)

        print(f"Finished preprocessing {video_folder}\n")

    print("Finished with Preprocessing Frames.")


