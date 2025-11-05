#!/usr/bin/env python3
"""
Cinematic Video Generator
Creates a professional cinematic video from images with:
- Ken Burns effect (zoom/pan)
- Smooth crossfade transitions
- Cinematic letterbox (2.39:1 aspect ratio)
- Color grading for cinematic look
- Professional timing
"""

import subprocess
import os
import glob

# Configuration
IMAGE_DIR = "images"
OUTPUT_VIDEO = "cinematic_video.mp4"
IMAGE_DURATION = 4.5  # seconds per image
TRANSITION_DURATION = 1.0  # crossfade duration
FPS = 30
WIDTH = 1920
HEIGHT = 1080
LETTERBOX_HEIGHT = int(HEIGHT / 2.39)  # Cinematic 2.39:1 aspect ratio

def get_images():
    """Get all images from the images directory"""
    image_patterns = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']
    images = []
    for pattern in image_patterns:
        images.extend(glob.glob(os.path.join(IMAGE_DIR, pattern)))
    images.sort()
    return images

def create_cinematic_video():
    """Create cinematic video with FFmpeg"""
    images = get_images()
    
    if not images:
        print("❌ No images found in the images directory!")
        return
    
    print(f"🎬 Creating cinematic video with {len(images)} images...")
    print(f"📸 Images: {[os.path.basename(img) for img in images]}")
    
    # Build FFmpeg filter complex for cinematic effects
    filter_parts = []
    
    # Process each image with Ken Burns effect and letterbox
    for i, img in enumerate(images):
        # Alternate between zoom in and zoom out for variety
        if i % 2 == 0:
            # Zoom in effect
            zoom_filter = f"zoompan=z='min(zoom+0.0015,1.2)':d={int(IMAGE_DURATION * FPS)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={WIDTH}x{HEIGHT}:fps={FPS}"
        else:
            # Zoom out effect
            zoom_filter = f"zoompan=z='if(lte(zoom,1.0),1.2,max(1.0,zoom-0.0015))':d={int(IMAGE_DURATION * FPS)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={WIDTH}x{HEIGHT}:fps={FPS}"
        
        # Add cinematic color grading and letterbox
        filter_parts.append(
            f"[{i}:v]{zoom_filter},"
            f"eq=contrast=1.1:brightness=0.0:saturation=0.9,"  # Cinematic color
            f"curves=vintage,"  # Film-like curve
            f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2,"  # Center
            f"drawbox=y=0:color=black@1:width=iw:height={(HEIGHT-LETTERBOX_HEIGHT)//2}:t=fill,"  # Top bar
            f"drawbox=y=ih-{(HEIGHT-LETTERBOX_HEIGHT)//2}:color=black@1:width=iw:height={(HEIGHT-LETTERBOX_HEIGHT)//2}:t=fill"  # Bottom bar
            f"[v{i}]"
        )
    
    # Create crossfade transitions between clips
    transition_parts = []
    current_label = "v0"
    
    for i in range(1, len(images)):
        next_label = f"vt{i}"
        offset = IMAGE_DURATION * i - TRANSITION_DURATION * i
        transition_parts.append(
            f"[{current_label}][v{i}]xfade=transition=fade:duration={TRANSITION_DURATION}:offset={offset}[{next_label}]"
        )
        current_label = next_label
    
    # Combine all filters
    filter_complex = ";".join(filter_parts + transition_parts)
    
    # Build FFmpeg command
    input_args = []
    for img in images:
        input_args.extend(["-loop", "1", "-t", str(IMAGE_DURATION), "-i", img])
    
    cmd = [
        "ffmpeg",
        "-y",  # Overwrite output
        *input_args,
        "-filter_complex", filter_complex,
        "-map", f"[{current_label}]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",  # High quality
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",  # Web optimization
        OUTPUT_VIDEO
    ]
    
    print(f"\n🎥 Rendering cinematic video...")
    print(f"⏱️  Estimated duration: {len(images) * IMAGE_DURATION - (len(images) - 1) * TRANSITION_DURATION:.1f} seconds")
    print(f"🎞️  Resolution: {WIDTH}x{HEIGHT} with 2.39:1 letterbox")
    print(f"✨ Effects: Ken Burns zoom, crossfade transitions, cinematic color grading")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"\n✅ Cinematic video created successfully: {OUTPUT_VIDEO}")
        
        # Get file size
        size_mb = os.path.getsize(OUTPUT_VIDEO) / (1024 * 1024)
        print(f"📦 File size: {size_mb:.2f} MB")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error creating video:")
        print(e.stderr)
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🎬 CINEMATIC VIDEO GENERATOR")
    print("=" * 60)
    create_cinematic_video()
    print("=" * 60)
