import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import threading
import logging
from function import CaptureText, save_text

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CaptureTextGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CaptureText - Trích xuất văn bản")
        self.root.geometry("800x600")
        self.capture = CaptureText()

        # Biến lưu trữ
        self.input_path = tk.StringVar()
        self.url = tk.StringVar()
        self.lang = tk.StringVar(value="en")
        self.model = tk.StringVar(value="base")
        self.frame_interval = tk.StringVar(value="30")
        self.is_processing = False

        # Tạo giao diện
        self.create_widgets()

    def create_widgets(self):
        # Khung chính
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Khung chọn đầu vào
        input_frame = ttk.LabelFrame(main_frame, text="Đầu vào", padding="5")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)

        ttk.Button(input_frame, text="Chọn video", command=lambda: self.select_file("video")).grid(row=0, column=0, padx=5)
        ttk.Button(input_frame, text="Chọn hình ảnh", command=lambda: self.select_file("image")).grid(row=0, column=1, padx=5)
        ttk.Button(input_frame, text="Chọn PDF", command=lambda: self.select_file("pdf")).grid(row=0, column=2, padx=5)
        ttk.Button(input_frame, text="Chọn âm thanh", command=lambda: self.select_file("audio")).grid(row=0, column=3, padx=5)

        ttk.Label(input_frame, text="URL:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(input_frame, textvariable=self.url, width=50).grid(row=1, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        # Khung tùy chọn
        options_frame = ttk.LabelFrame(main_frame, text="Tùy chọn", padding="5")
        options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(options_frame, text="Ngôn ngữ OCR:").grid(row=0, column=0, sticky=tk.W)
        ttk.Combobox(options_frame, textvariable=self.lang, values=["en", "vi", "fr", "es", "zh-CN"], state="readonly").grid(row=0, column=1, padx=5)

        ttk.Label(options_frame, text="Mô hình Whisper:").grid(row=0, column=2, sticky=tk.W)
        ttk.Combobox(options_frame, textvariable=self.model, values=["tiny", "base", "small", "medium"], state="readonly").grid(row=0, column=3, padx=5)

        ttk.Label(options_frame, text="Khoảng cách khung hình:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(options_frame, textvariable=self.frame_interval, width=10).grid(row=1, column=1, padx=5)

        # Khung hiển thị văn bản
        text_frame = ttk.LabelFrame(main_frame, text="Văn bản trích xuất", padding="5")
        text_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.rowconfigure(2, weight=1)

        self.text_area = tk.Text(text_frame, height=15, width=80, wrap=tk.WORD)
        self.text_area.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_area.yview)
        scrollbar.grid(row=0, column=4, sticky=(tk.N, tk.S))
        self.text_area.config(yscrollcommand=scrollbar.set)

        # Thanh tiến trình
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        self.progress.grid_remove()

        # Khung nút
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, sticky=tk.E, pady=5)

        ttk.Button(button_frame, text="Trích xuất", command=self.extract_text).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Lưu", command=self.save_output).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Xóa", command=self.clear_text).grid(row=0, column=2, padx=5)

    def select_file(self, file_type):
        """Chọn tệp dựa trên loại (video, image, pdf, audio)."""
        file_types = {
            "video": [("Video files", "*.mp4 *.avi *.mov"), ("All files", "*.*")],
            "image": [("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*")],
            "pdf": [("PDF files", "*.pdf"), ("All files", "*.*")],
            "audio": [("Audio files", "*.wav *.mp3"), ("All files", "*.*")]
        }
        file_path = filedialog.askopenfilename(filetypes=file_types[file_type])
        if file_path:
            self.input_path.set(file_path)
            self.url.set("")  # Xóa URL nếu chọn tệp
            logger.info(f"Đã chọn {file_type}: {file_path}")

    def extract_text(self):
        """Trích xuất văn bản từ đầu vào."""
        if self.is_processing:
            messagebox.showwarning("Cảnh báo", "Đang xử lý, vui lòng đợi!")
            return

        input_path = self.input_path.get()
        url = self.url.get()
        lang = self.lang.get()
        model = self.model.get()
        try:
            frame_interval = int(self.frame_interval.get())
        except ValueError:
            messagebox.showerror("Lỗi", "Khoảng cách khung hình phải là số nguyên!")
            return

        if not input_path and not url:
            messagebox.showerror("Lỗi", "Vui lòng chọn tệp hoặc nhập URL!")
            return

        # Bắt đầu xử lý trong luồng riêng
        self.is_processing = True
        self.progress.grid()
        self.progress.start()
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, "Đang xử lý...\n")

        def process():
            try:
                if url:
                    result = self.capture.extract_text_from_url(url)
                elif input_path.endswith((".mp4", ".avi", ".mov")):
                    result = self.capture.extract_text_from_video(input_path, frame_interval, lang)
                elif input_path.endswith((".png", ".jpg", ".jpeg")):
                    result = self.capture.extract_text_from_image(input_path, lang)
                elif input_path.endswith(".pdf"):
                    result = self.capture.extract_text_from_pdf(input_path)
                elif input_path.endswith((".wav", ".mp3")):
                    result = self.capture.transcribe_audio(input_path, model)
                else:
                    result = "Định dạng tệp không được hỗ trợ!"

                self.root.after(0, lambda: self.update_text_area(result))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi khi trích xuất: {e}"))
            finally:
                self.root.after(0, self.stop_processing)

        threading.Thread(target=process, daemon=True).start()

    def update_text_area(self, text):
        """Cập nhật khu vực văn bản với kết quả."""
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, text)

    def stop_processing(self):
        """Dừng thanh tiến trình và đặt lại trạng thái."""
        self.progress.stop()
        self.progress.grid_remove()
        self.is_processing = False

    def save_output(self):
        """Lưu văn bản vào tệp."""
        text = self.text_area.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Cảnh báo", "Không có văn bản để lưu!")
            return

        output_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if output_path:
            save_text(text, output_path)
            messagebox.showinfo("Thành công", f"Văn bản đã được lưu vào {output_path}")

    def clear_text(self):
        """Xóa khu vực văn bản."""
        self.text_area.delete(1.0, tk.END)
        self.input_path.set("")
        self.url.set("")

if __name__ == "__main__":
    root = tk.Tk()
    app = CaptureTextGUI(root)
    root.mainloop()
