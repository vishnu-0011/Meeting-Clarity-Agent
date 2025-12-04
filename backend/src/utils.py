# src/utils.py
import os
from moviepy import VideoFileClip
from PIL import Image

os.environ["FFMPEG_BINARY"] = r"C:\ffmpeg\bin\ffmpeg.exe"

def extract_media(video_path, output_dir="data/temp", fps=1):
    """Extracts audio and sampled frames from a video."""
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Audio Extraction
    clip = VideoFileClip(video_path)
    audio_path = os.path.join(output_dir, "audio.mp3")
    clip.audio.write_audiofile(audio_path, logger=None) # logger=None suppresses output
    
    # 2. Frame Extraction
    frame_dir = os.path.join(output_dir, "frames")
    os.makedirs(frame_dir, exist_ok=True)
    
    for t in range(0, int(clip.duration), int(1/fps)):
        frame = clip.get_frame(t)
        # Convert the NumPy array frame to a PIL Image and save
        Image.fromarray(frame).save(os.path.join(frame_dir, f"frame_{t:04d}.jpg"))
        
    clip.close()
    return audio_path, frame_dir, clip.duration