import argparse
import os
import cv2
import fitz
import moviepy.editor as mp
import easyocr
import whisper
import requests
import tempfile
from bs4 import BeautifulSoup
import logging

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CaptureText:
    """Lớp chính để trích xuất văn bản từ nhiều nguồn khác nhau."""
    
    @staticmethod
    def extract_audio_from_video(video_path, output_audio_path):
        """Trích xuất âm thanh từ video."""
        try:
            with mp.VideoFileClip(video_path) as clip:
                if clip.audio is None:
                    raise ValueError("Video không có âm thanh.")
                clip.audio.write_audiofile(output_audio_path)
                logger.info(f"Đã trích xuất âm thanh: {output_audio_path}")
        except Exception as e:
            logger.error(f"Lỗi khi trích xuất âm thanh từ {video_path}: {e}")
            raise

    @staticmethod
    def extract_frames_from_video(video_path, frame_interval=30):
        """Trích xuất các khung hình từ video."""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError("Không thể mở video.")
            frames = []
            count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if count % frame_interval == 0:
                    frames.append(frame)
                count += 1
            cap.release()
            logger.info(f"Đã trích xuất {len(frames)} khung hình từ {video_path}")
            return frames
        except Exception as e:
            logger.error(f"Lỗi khi trích xuất khung hình từ {video_path}: {e}")
            raise

    @staticmethod
    def extract_text_from_image(image, lang='en', is_frame=False):
        """Trích xuất văn bản từ hình ảnh hoặc khung hình OpenCV."""
        try:
            reader = easyocr.Reader([lang])
            if is_frame:
                # Lưu khung hình tạm thời nếu là khung hình OpenCV
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    cv2.imwrite(tmp.name, image)
                    result = reader.readtext(tmp.name)
                    os.remove(tmp.name)
            else:
                result = reader.readtext(image)
            extracted_text = ' '.join([text[1] for text in result])
            logger.info(f"Đã trích xuất văn bản từ  từ hình ảnh.")
            return extracted_text
        except Exception as e:
            logger.error(f"Lỗi khi trích xuất văn bản từ hình ảnh: {e}")
            return ""

    @staticmethod
    def extract_text_from_pdf(pdf_path):
        """Trích xuất văn bản từ PDF."""
        try:
            doc = fitz.open(pdf_path)
            extracted_text = ""
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                extracted_text += page.get_text()
            doc.close()
            logger.info(f"Đã trích xuất văn bản từ {pdf_path}")
            return extracted_text
        except Exception as e:
            logger.error(f"Lỗi khi trích xuất văn bản từ {pdf_path}: {e}")
            return ""

    @staticmethod
    def extract_text_from_url(url):
        """Trích xuất văn bản từ trang web."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            for script in soup(["script", "style", "noscript"]):
                script.decompose()
            text = soup.get_text(separator=' ', strip=True)
            logger.info(f"Đã trích xuất văn bản từ {url}")
            return text
        except Exception as e:
            logger.error(f"Lỗi khi trích xuất văn bản từ {url}: {e}")
            return ""

    @staticmethod
    def transcribe_audio(audio_path, model_name="base"):
        """Chuyển đổi âm thanh thành văn bản."""
        try:
            model = whisper.load_model(model_name)
            result = model.transcribe(audio_path)
            logger.info(f"Đã chuyển đổi âm thanh từ {audio_path}")
            return result["text"]
        except Exception as e:
            logger.error(f"Lỗi khi chuyển đổi âm thanh từ {audio_path}: {e}")
            return ""

    @classmethod
    def extract_text_from_video(cls, video_path, frame_interval=30, lang='en'):
        """Trích xuất văn bản từ video (âm thanh và khung hình)."""
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio:
                audio_path = tmp_audio.name
                cls.extract_audio_from_video(video_path, audio_path)
                audio_text = cls.transcribe_audio(audio_path)
            frames = cls.extract_frames_from_video(video_path, frame_interval)
            image_texts = [cls.extract_text_from_image(frame, lang, is_frame=True) for frame in frames]
            full_text = audio_text + "\n" + "\n".join([t for t in image_texts if t])
            os.remove(audio_path)
            logger.info(f"Đã trích xuất văn bản từ video {video_path}")
            return full_text
        except Exception as e:
            logger.error(f"Lỗi khi trích xuất văn bản từ video {video_path}: {e}")
            if os.path.exists(audio_path):
                os.remove(audio_path)
            return ""

def save_text(text, output_path):
    """Lưu văn bản vào tệp."""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        logger.info(f"Đã lưu văn bản vào {output_path}")
    except Exception as e:
        logger.error(f"Lỗi khi lưu văn bản vào {output_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="CaptureText: Trích xuất văn bản từ video, hình ảnh, PDF, URL, hoặc âm thanh.")
    parser.add_argument("--video", help="Đường dẫn đến tệp video")
    parser.add_argument("--image", help="Đường dẫn đến tệp hình ảnh")
    parser.add_argument("--pdf", help="Đường dẫn đến tệp PDF")
    parser.add_argument("--url", help="URL của trang web")
    parser.add_argument("--audio", help="Đường dẫn đến tệp âm thanh")
    parser.add_argument("--output", help="Đường dẫn đến tệp đầu ra (mặc định: in ra màn hình)")
    parser.add_argument("--lang", default="en", help="Ngôn ngữ cho OCR (mặc định: en)")
    parser.add_argument("--frame-interval", type=int, default=30, help="Khoảng cách khung hình khi trích xuất từ video")
    parser.add_argument("--model", default="base", help="Mô hình Whisper cho chuyển đổi âm thanh (mặc định: base)")

    args = parser.parse_args()

    capture = CaptureText()
    result = ""

    if args.video:
        result = capture.extract_text_from_video(args.video, args.frame_interval, args.lang)
    elif args.image:
        result = capture.extract_text_from_image(args.image, args.lang)
    elif args.pdf:
        result = capture.extract_text_from_pdf(args.pdf)
    elif args.url:
        result = capture.extract_text_from_url(args.url)
    elif args.audio:
        result = capture.transcribe_audio(args.audio, args.model)
    else:
        parser.print_help()
        return

    if args.output:
        save_text(result, args.output)
    else:
        print("Extracted Text:")
        print(result)

if __name__ == "__main__":
    main()
