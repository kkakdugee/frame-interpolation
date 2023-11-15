import os
import cv2
import torch
import numpy as np
from frame_interpolator import FrameInterpolator
import re

# Function to sort filenames numerically which helps in maintaining the order of frames
def numerical_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

# Function to load a frame from file and preprocess it for the model
def load_frame(frame_path):
    frame = cv2.imread(frame_path)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert from BGR to RGB
    frame = frame.transpose((2, 0, 1)) / 255.0  # Normalize and transpose to channel first format
    return frame

# Function to perform frame interpolation and save the resulting frame
def interpolate_and_save(model, device, frame_a, frame_b, temp_dir, i, m):
    # Prepare the tensors for the model
    frame_a_tensor = torch.from_numpy(frame_a).unsqueeze(0).float().to(device)
    frame_b_tensor = torch.from_numpy(frame_b).unsqueeze(0).float().to(device)
    input_tensor = torch.cat((frame_a_tensor, frame_b_tensor), 1)

    # Perform inference
    with torch.no_grad():
        output_tensor = model(input_tensor)
    # Process the output and save the frame
    output_frame = output_tensor.squeeze().cpu().numpy()
    output_frame = output_frame.transpose((1, 2, 0))  # Transpose back to height x width x channel
    output_frame = np.clip(output_frame, 0, 1)  # Clip values to maintain valid range
    output_frame = (output_frame * 255).astype(np.uint8)  # Denormalize to 0-255 range
    output_frame_bgr = cv2.cvtColor(output_frame, cv2.COLOR_RGB2BGR)  # Convert back to BGR for saving
    
    # Save the frame to the temporary directory
    interpolated_frame_path = os.path.join(temp_dir, f'interpolated_frame_{m + 1}_{i}.jpg')
    cv2.imwrite(interpolated_frame_path, output_frame_bgr)
    return interpolated_frame_path

# Main function to control the frame interpolation process
def main(multiplier, video_name, video_folder, video_fps):
    frames_dir = f'./data/raw_frames/{video_folder}'
    temp_dir = './data/temp_interpolated_frames'
    os.makedirs(temp_dir, exist_ok=True)  # Create the temporary directory if it doesn't exist

    # Sort the frame files to ensure they are in the correct order
    frame_files = sorted([os.path.join(frames_dir, f) for f in os.listdir(frames_dir) if f.endswith('.jpg')],
                         key=numerical_sort_key)

    # Set up the device for PyTorch and load the trained model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = FrameInterpolator().to(device)
    model.load_state_dict(torch.load('./models/frame_interpolator_final.pth'))
    model.eval()

    original_fps = video_fps  # Original frame rate
    target_fps = original_fps * (2 ** multiplier)  # Target frame rate after interpolation

    first_frame = cv2.imread(frame_files[0])
    height, width, layers = first_frame.shape
    video_path = f"./output/{video_folder}_{target_fps}fps.mp4"

    print(f"Interpolating from {original_fps} fps to {target_fps} fps.")

    # Start the interpolation process
    interpolated_frame_files = frame_files.copy()  # Copy the original frames
    for m in range(multiplier):

        print(f"Starting pass through {m + 1}/{multiplier}.")

        # Interpolate frames and add them to the new sequence
        new_interpolated_frames = []
        for i in range(len(interpolated_frame_files) - 1):
            frame_a = load_frame(interpolated_frame_files[i])
            frame_b = load_frame(interpolated_frame_files[i + 1])
            # Save the interpolated frame and add it to the list
            interpolated_frame = interpolate_and_save(
                model, device, frame_a, frame_b, temp_dir, i, m
            )
            new_interpolated_frames.extend([interpolated_frame_files[i], interpolated_frame])
        # Add the last frame to the new sequence
        new_interpolated_frames.append(interpolated_frame_files[-1])
        interpolated_frame_files = new_interpolated_frames

    # Set up the video writer to save the output video
    video = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'mp4v'), target_fps, (width, height))

    # Write each frame to the output video file
    for frame_path in interpolated_frame_files:
        video.write(cv2.imread(frame_path))

    video.release()  # Release the video writer
    print(f"Interpolation complete. Video saved as {video_path}")

    # Clean up the temporary files created during interpolation
    for file in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file))
    os.rmdir(temp_dir)  # Remove the temporary directory
    print("Temporary files cleaned up.")


