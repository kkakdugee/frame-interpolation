import os, sys
HERE = os.path.dirname(__file__)  
SRC  = os.path.abspath(os.path.join(HERE, "src"))
sys.path.insert(0, SRC)

import streamlit as st
from src.data.video_utils import read_uploaded_video
from src.interpolation_utils import naive_interpolate, deep_interpolate
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
st.set_page_config(
    page_title="AI Frame Interpolation Studio", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .step-container {
        border: 2px solid #f0f2f6;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        background-color: #fafafa;
        color: black;
    }
    .step-number {
        background: #667eea;
        color: white;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 10px;
    }
    .result-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: white;
    }
    .info-box {
        background: #e3f2fd;
        color: black;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    .info-box h3, .info-box p { color: black; }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🎬 AI Frame Interpolation Studio</h1>
    <p>Transform your videos with smooth motion using advanced interpolation techniques</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for controls and information
with st.sidebar:
    st.header("🎛️ Controls")
    
    # Video upload section
    st.subheader("📁 Upload Video")
    df = st.file_uploader(
        "Choose a video file", 
        type=["mp4", "avi", "mov"],
        help="Supported formats: MP4, AVI, MOV"
    )
    
    if df:
        st.success(f"✅ Uploaded: {df.name}")
        
        # Parameters section
        st.subheader("⚙️ Parameters")
        num_iters = st.number_input(
            "Interpolation passes:", 
            min_value=1, 
            max_value=5, 
            value=1, 
            step=1,
            help="Each pass doubles the frame rate. More passes = smoother video but longer processing time."
        )
        
        # Show expected FPS increase
        original_fps_placeholder = st.empty()
        output_fps_placeholder = st.empty()
        
        st.subheader("ℹ️ How it works")
        st.markdown("""
        **Naive Interpolation**: Simple pixel averaging between frames
        
        **Deep Learning**: AI model predicts realistic intermediate frames
        
        **Tips**:
        - Start with 1-2 passes for testing
        - Higher passes = longer processing time
        - Works best with smooth motion videos
        """)

# Main content area
if not df:
    # Welcome screen
    st.markdown("""
    <div class="info-box">
        <h3>🚀 Get Started</h3>
        <p>Upload a video file using the sidebar to begin. This tool will create smooth interpolated frames between existing frames, effectively increasing your video's frame rate and creating smoother motion.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **📤 Step 1: Upload**
        
        Choose your video file from the sidebar
        """)
    with col2:
        st.markdown("""
        **⚙️ Step 2: Configure**
        
        Set interpolation parameters
        """)
    with col3:
        st.markdown("""
        **🎬 Step 3: Process**
        
        Generate and compare results
        """)
    
    st.stop()

# Process uploaded video
st.markdown("""
<div class="step-container">
    <span class="step-number">1</span>
    <strong>Video Analysis</strong>
</div>
""", unsafe_allow_html=True)

# Save original file to disk
orig_filename = f"original_{df.name}"
with open(orig_filename, "wb") as f:
    f.write(df.read())

# Load original clip to extract fps and audio
try:
    orig_clip = VideoFileClip(orig_filename)
    fps = orig_clip.fps
    audio = orig_clip.audio
    duration = orig_clip.duration
except Exception:
    fps = 30
    audio = None
    duration = None

# Update sidebar with video info
with st.sidebar:
    original_fps_placeholder.metric("Original FPS", f"{fps:.1f}")
    fps_out = fps * (2 ** num_iters)
    output_fps_placeholder.metric("Output FPS", f"{fps_out:.1f}", f"+{fps_out-fps:.1f}")

# Read all frames as PIL images
with st.spinner("📖 Reading video frames..."):
    frames = read_uploaded_video(orig_filename)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📹 Total Frames", len(frames))
with col2:
    st.metric("⏱️ Duration", f"{duration:.1f}s" if duration else "Unknown")
with col3:
    st.metric("📏 Resolution", f"{frames[0].size[0]}x{frames[0].size[1]}")

# Original video preview
st.markdown("""
<div class="step-container">
    <span class="step-number">2</span>
    <strong>Original Video Preview</strong>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])
with col1:
    embed_video(orig_filename, width=500)
with col2:
    st.markdown(f"""
    **Video Information:**
    - **Frames:** {len(frames)}
    - **FPS:** {fps:.1f}
    - **Duration:** {duration:.1f}s
    - **Resolution:** {frames[0].size[0]}×{frames[0].size[1]}
    
    **After Interpolation:**
    - **New FPS:** {fps_out:.1f}
    - **Smoothness Increase:** {2**num_iters}x
    """)

# Frame analysis section
st.markdown("""
<div class="step-container">
    <span class="step-number">3</span>
    <strong>Frame-by-Frame Preview</strong>
</div>
""", unsafe_allow_html=True)

idx = st.slider(
    "Select frame pair to preview interpolation:", 
    0, 
    max(0, len(frames) - 2), 
    0,
    help="Choose any two consecutive frames to see how interpolation works"
)

# Display original frames
st.subheader("📋 Original Consecutive Frames")
col1, col2 = st.columns(2)
orig_frame_a = frames[idx]
orig_frame_b = frames[idx+1]

with col1:
    st.image(orig_frame_a, caption=f"Frame {idx}", use_column_width=True)
with col2:
    st.image(orig_frame_b, caption=f"Frame {idx+1}", use_column_width=True)

# Generate and display interpolated frames
st.subheader("🔄 Interpolated Results")

col1, col2 = st.columns(2)

with col1:
    with st.container():
        # st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown("**🔢 Naive Interpolation (Pixel Average)**")
        
        with st.spinner("Generating naive interpolation..."):
            naive_img = naive_interpolate(orig_frame_a, orig_frame_b)
            naive_img = naive_img.resize(orig_frame_a.size)
        
        st.image(naive_img, caption="Simple pixel averaging", use_column_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

with col2:
    with st.container():
        # st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown("**🧠 Deep Learning Interpolation**")
        
        try:
            with st.spinner("Generating AI interpolation..."):
                deep_img = deep_interpolate(orig_frame_a, orig_frame_b)
                deep_img = deep_img.resize(orig_frame_a.size)
            
            st.image(deep_img, caption="AI-generated intermediate frame", use_column_width=True)
        except Exception as e:
            st.error(f"⚠️ Deep interpolation error: {e}")
            st.info("This could be due to model loading issues or system requirements.")
        
        st.markdown("</div>", unsafe_allow_html=True)

# Video generation section
st.markdown("""
<div class="step-container">
    <span class="step-number">4</span>
    <strong>Generate Complete Videos</strong>
</div>
""", unsafe_allow_html=True)

st.info("🎬 Ready to generate full interpolated videos? This process may take several minutes depending on video length and interpolation passes.")

if st.button("🚀 Generate Interpolated Videos", type="primary"):
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Generate naive interpolation
    status_text.text("🔢 Generating naive interpolation...")
    progress_bar.progress(25)
    
    naive_frames = iterative_interpolate(frames, naive_interpolate, num_iters)
    naive_clip = ImageSequenceClip([np.array(f) for f in naive_frames], fps=fps_out)
    naive_final = f"naive_out_{df.name}"
    
    progress_bar.progress(50)
    
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
    status_text.text("🧠 Generating deep learning interpolation...")
    progress_bar.progress(75)
    
    try:
        deep_frames = iterative_interpolate(frames, deep_interpolate, num_iters)
        orig_size = frames[0].size
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
        
        progress_bar.progress(100)
        status_text.text("✅ Video generation complete!")
        
        # Display results
        st.success("🎉 Interpolation complete! Compare the results below:")
        
        st.subheader("📊 Results Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown("**🔢 Naive Interpolation Result**")
            embed_video(naive_final, width=400)
            st.caption(f"FPS: {fps_out:.1f} | Method: Pixel averaging")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            # st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown("**🧠 Deep Learning Result**")
            embed_video(deep_final, width=400)
            st.caption(f"FPS: {fps_out:.1f} | Method: AI interpolation")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Analysis
        st.subheader("📈 Analysis")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Original Frame Count", len(frames))
        with col2:
            st.metric("Interpolated Frame Count", len(naive_frames), f"+{len(naive_frames) - len(frames)}")
        with col3:
            st.metric("Smoothness Improvement", f"{2**num_iters}x")
            
    except Exception as e:
        progress_bar.progress(100)
        status_text.text("⚠️ Deep learning interpolation failed")
        st.error(f"Deep interpolation error: {e}")
        
        # Show only naive result
        st.subheader("📊 Naive Interpolation Result")
        embed_video(naive_final, width=600)
        st.caption(f"FPS: {fps_out:.1f} | Method: Pixel averaging")

# Footer
st.markdown("---")