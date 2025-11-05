#!/usr/bin/env python3
"""
Cinematic Video Generator
Creates a professional cinematic video from images with:
- Ken Burns effect (zoom/pan)
- Smooth crossfade transitions
- Cinematic letterbox (2.39:1 aspect ratio)
- Color grading for cinematic look
- Professional pacing
"""

import subprocess
import os
import glob

# Configuration
IMAGE_DIR = "images"
OUTPUT_VIDEO = "cinematic_video.mp4"
IMAGE_DURATION = 5  # seconds per image
TRANSITION_DURATION = 1.5  # crossfade duration
FPS = 30
WIDTH = 1920
HEIGHT = 1080

def get_image_files():
    """Get all image files from the images directory"""
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']
    images = []
    for ext in image_extensions:
        images.extend(glob.glob(os.path.join(IMAGE_DIR, ext)))
    images.sort()
    return images

def create_cinematic_video():
    """Generate cinematic video using FFmpeg"""
    images = get_image_files()
    
    if not images:
        print("❌ No images found in the images directory!")
        return False
    
    print(f"🎬 Creating cinematic video from {len(images)} images...")
    print(f"📸 Images: {[os.path.basename(img) for img in images]}")
    
    # Build FFmpeg filter complex for cinematic effects
    filter_parts = []
    
    # Process each image with Ken Burns effect and cinematic color grading
    for i, img in enumerate(images):
        # Alternate between zoom in and zoom out for variety
        if i % 2 == 0:
            # Zoom in effect
            zoom_expr = "if(lte(zoom,1.0),1.0,max(1.3,zoom-0.0015))"
        else:
            # Zoom out effect  
            zoom_expr = "if(lte(zoom,1.0),1.3,max(1.0,zoom-0.0015))"
        
        # Create Ken Burns effect with color grading
        filter_parts.append(
            f"[{i}:v]scale=3840:2160:force_original_aspect_ratio=increase,"
            f"crop=1920:1080,"
            f"zoompan=z='{zoom_expr}':d={int(IMAGE_DURATION * FPS)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':fps={FPS}:s={WIDTH}x{HEIGHT},"
            f"eq=contrast=1.15:brightness=-0.03:saturation=0.85:gamma=1.1,"
            f"format=yuv420p[v{i}]"
        )
    
    # Create crossfade transitions between clips
    transition_parts = []
    if len(images) == 1:
        # Single image - no transitions needed
        last_output = "[v0]"
    else:
        # Multiple images - create crossfade chain
        for i in range(len(images) - 1):
            offset = (i + 1) * IMAGE_DURATION - (i + 1) * TRANSITION_DURATION
            if i == 0:
                # First transition
                transition_parts.append(
                    f"[v0][v1]xfade=transition=fade:duration={TRANSITION_DURATION}:offset={offset}[vx1]"
                )
            else:
                # Subsequent transitions
                transition_parts.append(
                    f"[vx{i}][v{i+1}]xfade=transition=fade:duration={TRANSITION_DURATION}:offset={offset}[vx{i+1}]"
                )
        
        # Use the last transition output
        last_output = f"[vx{len(images)-1}]"
    
    # Add cinematic letterbox bars (2.39:1 aspect ratio)
    letterbox_height = int(HEIGHT / 2.39)
    bar_height = (HEIGHT - letterbox_height) // 2
    
    final_filter = (
        f"{last_output}"
        f"drawbox=y=0:color=black:width=iw:height={bar_height}:t=fill,"
        f"drawbox=y=ih-{bar_height}:color=black:width=iw:height={bar_height}:t=fill[outv]"
    )
    
    # Combine all filter parts
    all_filters = filter_parts + transition_parts + [final_filter]
    filter_complex = ";".join(all_filters)
    
    # Build FFmpeg command
    input_args = []
    for img in images:
        input_args.extend(["-loop", "1", "-t", str(IMAGE_DURATION), "-i", img])
    
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",  # Overwrite output file
        *input_args,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        OUTPUT_VIDEO
    ]
    
    print("\n🎥 Rendering cinematic video...")
    print("⏳ This may take a minute...\n")
    
    try:
        result = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Cinematic video created successfully: {OUTPUT_VIDEO}")
        
        # Get video info
        probe_cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration,size",
            "-of", "default=noprint_wrappers=1",
            OUTPUT_VIDEO
        ]
        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
        print(f"\n📊 Video Info:")
        print(probe_result.stdout)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating video:")
        print(e.stderr)
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🎬 CINEMATIC VIDEO GENERATOR 🎬")
    print("=" * 60)
    print()
    
    success = create_cinematic_video()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 Your cinematic video is ready!")
        print(f"📁 Location: {OUTPUT_VIDEO}")
        print("=" * 60)
    else:
        print("\n❌ Failed to create video")
        exit(1)
