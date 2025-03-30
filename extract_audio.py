import moviepy.editor as mp
import sys

def extract_audio(video_path, output_audio_path):
    video = mp.VideoFileClip(video_path)
    video.audio.write_audiofile(output_audio_path)
    print(f"Audio extracted: {output_audio_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python extract_audio.py <input_video> <output_audio>")
    else:
        extract_audio(sys.argv[1], sys.argv[2])
