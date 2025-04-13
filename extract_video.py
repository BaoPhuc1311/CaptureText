import os
import cv2
import moviepy.editor as mp
from src.speech_to_text import transcribe_audio
from src.extract_image import extract_text_from_image
import tempfile

def extract_audio_from_video(video_path, output_audio_path):
    clip = mp.VideoFileClip(video_path)
    clip.audio.write_audiofile(output_audio_path)

def extract_frames_from_video(video_path, frame_interval=30):
    cap = cv2.VideoCapture(video_path)
    frames = []
    count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if count % frame_interval == 0:
            frames.append(frame)
        count += 1
    cap.release()
    return frames

def extract_text_from_video(video_path):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio:
        audio_path = tmp_audio.name
    extract_audio_from_video(video_path, audio_path)
    audio_text = transcribe_audio(audio_path)
    frames = extract_frames_from_video(video_path)
    image_texts = [extract_text_from_image(frame) for frame in frames]
    full_text = audio_text + "\n" + "\n".join(image_texts)
    os.remove(audio_path)
    return full_text

if __name__ == "__main__":
    video_file = "example.mp4"
    result = extract_text_from_video(video_file)
    print(result)
