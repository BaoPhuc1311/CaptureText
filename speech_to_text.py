import whisper
import sys

def transcribe_audio(audio_path, output_text_path):
    model = whisper.load_model("base")  # Chọn mô hình phù hợp
    result = model.transcribe(audio_path)

    with open(output_text_path, "w", encoding="utf-8") as f:
        f.write(result["text"])

    print(f"✅ Transcription saved: {output_text_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python speech_to_text.py <input_audio> <output_text>")
    else:
        transcribe_audio(sys.argv[1], sys.argv[2])
