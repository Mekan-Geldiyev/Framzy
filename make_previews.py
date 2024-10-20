from moviepy.editor import VideoFileClip

def create_preview(input_video_path, output_preview_path, preview_duration=10):
    # Load the video
    clip = VideoFileClip(input_video_path)

    # Determine the start time and end time for the preview
    start_time = max(0, (clip.duration - preview_duration) / 2)
    end_time = start_time + preview_duration

    # Create the preview clip
    preview_clip = clip.subclip(start_time, end_time)

    # Save the preview clip
    preview_clip.write_videofile(output_preview_path, codec='libx264', fps=30)

    # Close the clip to release resources
    preview_clip.close()

# Example usage
input_video_path = "5minutecraft_clip1.mp4"
output_preview_path = "PREVIEW5minutecraft_clip1.mp4"
create_preview(input_video_path, output_preview_path, preview_duration=15)
