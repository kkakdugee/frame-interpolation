import os
import streamlit as st
from src.data.video_utils import read_uploaded_video
from src.interpolation_utils import naive_interpolate, deep_interpolate
import cv2
import numpy as np
import base64
from moviepy import VideoFileClip, ImageSequenceClip

# Embed video via HTML with fixed width
def embed_video(path: str, width: int = 300):
    ext = os.path.splitext(path)[1].lower().lstrip('.')
    with open(path, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    html = (
        f"<video width=\"{width}\" controls>"
        f"<source src=\"data:video/{ext};base64,{b64}\" type=\"video/{ext}\">"
        "</video>"
    )
    st.markdown(html, unsafe_allow_html=True)

# Build intermediate frames iteratively
def iterative_interpolate(frames, interp_func, iterations):
    frames_out = frames
    for _ in range(iterations):
        new_frames = []
        for i in range(len(frames_out) - 1):
            new_frames.append(frames_out[i])
            new_frames.append(interp_func(frames_out[i], frames_out[i+1]))
        new_frames.append(frames_out[-1])
        frames_out = new_frames
    return frames_out

# Streamlit UI setup
st.set_page_config(page_title="Frame Interpolation Demo", layout="wide")
st.title("Frame Interpolation: Naive vs Deep Learning")

# Video upload
df = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov"])
if not df:
    st.info("Please upload a video to begin interpolation.")
    st.stop()

# Save original file to disk
orig_filename = f"original_{df.name}"
with open(orig_filename, "wb") as f:
    f.write(df.read())

# Load original clip to extract fps and audio
try:
    orig_clip = VideoFileClip(orig_filename)
    fps = orig_clip.fps
    audio = orig_clip.audio
except Exception:
    fps = 30
    audio = None

# User input: number of interpolation passes
num_iters = st.number_input(
    "Interpolation passes (each doubles FPS):", min_value=1, max_value=5, value=1, step=1
)
# Compute output FPS
fps_out = fps * (2 ** num_iters)

# Read all frames as PIL images
frames = read_uploaded_video(orig_filename)
st.success(f"Loaded {len(frames)} frames from video.")

# Create tabs for comparison and frame analysis
tab1, tab2 = st.tabs(["Video Comparison", "Frame Analysis"])

with tab1:
    st.header("Video Comparison")

    # Show original video at top
    st.subheader("Original Video")
    embed_video(orig_filename, width=600)
    st.caption(f"Original FPS: {fps:.1f}")

    if st.button("Generate comparison videos"):
        # Generate naive interpolation
        naive_frames = iterative_interpolate(frames, naive_interpolate, num_iters)
        naive_clip = ImageSequenceClip([np.array(f) for f in naive_frames], fps=fps_out)
        naive_final = f"naive_out_{df.name}"
        if audio:
            naive_clip.write_videofile(
                naive_final,
                codec="libx264",
                audio=audio,
                audio_codec="aac"
            )
        else:
            naive_clip.write_videofile(
                naive_final,
                codec="libx264",
                audio=False
            )

        # Generate deep interpolation
        deep_frames = iterative_interpolate(frames, deep_interpolate, num_iters)
        # Resize deep frames to match original resolution
        orig_size = frames[0].size  # (width, height)
        deep_frames = [f.resize(orig_size) for f in deep_frames]
        deep_clip = ImageSequenceClip([np.array(f) for f in deep_frames], fps=fps_out)
        deep_final = f"deep_out_{df.name}"
        if audio:
            deep_clip.write_videofile(
                deep_final,
                codec="libx264",
                audio=audio,
                audio_codec="aac"
            )
        else:
            deep_clip.write_videofile(
                deep_final,
                codec="libx264",
                audio=False
            )

        # Display side-by-side
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Naive Interpolation")
            embed_video(naive_final, width=300)
            st.caption(f"Output FPS: {fps_out:.1f}")
        with col2:
            st.subheader("Deep Learning Interpolation")
            embed_video(deep_final, width=300)
            st.caption(f"Output FPS: {fps_out:.1f}")

with tab2:
    st.header("Frame-by-Frame Analysis")
    idx = st.slider("Select starting frame index:", 0, max(0, len(frames) - 2), 0)
    # Display frames scaled to a fixed width (maintains aspect ratio)
    display_width = 600
    orig_frame_a = frames[idx]
    orig_frame_b = frames[idx+1]

    c1, c2 = st.columns(2)
    with c1:
        st.image(orig_frame_a, caption=f"Original Frame {idx}", width=display_width)
    with c2:
        st.image(orig_frame_b, caption=f"Original Frame {idx+1}", width=display_width)

    st.markdown("---")

    # Generate and display interpolated frames
    naive_img = naive_interpolate(orig_frame_a, orig_frame_b)
    # Ensure naive matches original size (usually already does)
    naive_img = naive_img.resize(orig_frame_a.size)
    try:
        deep_img = deep_interpolate(orig_frame_a, orig_frame_b)
        # Resize deep output to original frame size to preserve aspect ratio
        deep_img = deep_img.resize(orig_frame_a.size)
    except Exception as e:
        deep_img = None
        st.warning(f"Deep interpolation error: {e}")

    rr1, rr2 = st.columns(2)
    with rr1:
        st.subheader("Naive (Pixel Average)")
        st.image(naive_img, caption="Interpolated (Naive)", width=display_width)
    with rr2:
        st.subheader("Deep Learning Model")
        if deep_img:
            st.image(deep_img, caption="Interpolated (Deep)", width=display_width)
        else:
            st.warning("Deep interpolation not available.")