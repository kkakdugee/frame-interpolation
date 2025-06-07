import cv2
from PIL import Image
import tempfile
from typing import List

def read_uploaded_video(video_file) -> List[Image.Image]:
    """
    Reads a user-uploaded video file into a list of PIL Images.

    Args:
        video_file: file-like object or path to video
    Returns:
        List of frames as PIL Images (RGB).
    """
    # Handle file-like object
    if hasattr(video_file, 'read'):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        tmp.write(video_file.read())
        tmp.flush()
        cap = cv2.VideoCapture(tmp.name)
    else:
        cap = cv2.VideoCapture(str(video_file))

    frames: List[Image.Image] = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Convert BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        frames.append(img)
    cap.release()
    return frames