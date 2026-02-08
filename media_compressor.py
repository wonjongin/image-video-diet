import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import subprocess
from pathlib import Path
import threading

# HEIC 지원을 위한 import
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIC_SUPPORTED = True
except ImportError:
    HEIC_SUPPORTED = False

class MediaCompressor:
    # 압축된 파일에 붙일 prefix (원본 파일명 앞에 붙음)
    OUTPUT_PREFIX = "압축_"

    def __init__(self, root):
        self.root = root
        self.root.title("이미지/동영상 용량 줄이기 v1.0.0")
        self.root.geometry("600x400")

        # 폴더 선택 프레임
        folder_frame = tk.Frame(root, pady=10)
        folder_frame.pack(fill=tk.X, padx=20)

        tk.Label(folder_frame, text="폴더:").pack(side=tk.LEFT)
        self.folder_path = tk.StringVar()
        tk.Entry(folder_frame, textvariable=self.folder_path, width=50).pack(side=tk.LEFT, padx=10)
        tk.Button(folder_frame, text="찾아보기", command=self.select_folder).pack(side=tk.LEFT)

        # 옵션 프레임
        option_frame = tk.LabelFrame(root, text="압축 옵션", pady=10)
        option_frame.pack(fill=tk.X, padx=20, pady=10)

        # 이미지 목표 크기
        tk.Label(option_frame, text="이미지 목표 크기 (KB):").grid(row=0, column=0, padx=10, sticky=tk.W)
        self.target_size = tk.IntVar(value=300)
        tk.Entry(option_frame, textvariable=self.target_size, width=10).grid(row=0, column=1, sticky=tk.W)

        # 이미지 최대 해상도
        tk.Label(option_frame, text="이미지 최대 해상도 (px):").grid(row=1, column=0, padx=10, sticky=tk.W)
        self.max_resolution = tk.IntVar(value=2000)
        tk.Entry(option_frame, textvariable=self.max_resolution, width=10).grid(row=1, column=1, sticky=tk.W)

        # 동영상 최대 해상도
        tk.Label(option_frame, text="동영상 최대 높이 (px):").grid(row=2, column=0, padx=10, sticky=tk.W)
        self.max_video_height = tk.IntVar(value=1080)
        tk.Entry(option_frame, textvariable=self.max_video_height, width=10).grid(row=2, column=1, sticky=tk.W)

        # 하위 폴더 포함 옵션
        self.recursive = tk.BooleanVar(value=True)
        tk.Checkbutton(option_frame, text="하위 폴더 포함", variable=self.recursive).grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=10)

        # 시작 버튼
        self.start_button = tk.Button(root, text="압축 시작", command=self.start_compression, bg="green", fg="white", font=("Arial", 12, "bold"))
        self.start_button.pack(pady=10)

        # 진행 상황 프레임
        progress_frame = tk.LabelFrame(root, text="진행 상황", pady=10)
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 진행률 표시
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.pack(fill=tk.X, padx=10, pady=5)

        # 로그 텍스트
        self.log_text = tk.Text(progress_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        scrollbar = tk.Scrollbar(self.log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()

    def compress_image(self, image_path, target_kb=300, max_resolution=1920):
        """이미지를 목표 크기로 압축"""
        try:
            img = Image.open(image_path)
            original_resolution = f"{img.width}x{img.height}"

            # 해상도 조절 (긴 쪽이 max_resolution보다 크면 축소)
            max_dimension = max(img.width, img.height)
            if max_dimension > max_resolution:
                ratio = max_resolution / max_dimension
                new_width = int(img.width * ratio)
                new_height = int(img.height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                resolution_changed = True
            else:
                resolution_changed = False

            # RGBA 이미지를 RGB로 변환 (JPEG 저장을 위해)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # 원본 파일 크기
            original_size = os.path.getsize(image_path) / 1024

            # 출력 파일 경로 (원본 폴더에 prefix를 붙여 저장)
            original_path = Path(image_path)
            output_filename = self.OUTPUT_PREFIX + original_path.stem + '.jpg'
            output_path = str(original_path.parent / output_filename)

            # 품질을 조정하면서 목표 크기에 맞춤
            quality = 85
            while quality > 5:
                img.save(output_path, 'JPEG', quality=quality, optimize=True)
                current_size = os.path.getsize(output_path) / 1024

                if current_size <= target_kb * 1.1:  # 10% 여유
                    break

                quality -= 5

            final_size = os.path.getsize(output_path) / 1024
            reduction = ((original_size - final_size) / original_size) * 100

            resolution_info = f" [{original_resolution}→{img.width}x{img.height}]" if resolution_changed else ""

            # 이미 목표 크기보다 작았지만 해상도는 조절된 경우
            if original_size <= target_kb and resolution_changed:
                return f"✓ {os.path.basename(image_path)}: {original_size:.1f}KB → {final_size:.1f}KB{resolution_info}"
            elif original_size <= target_kb:
                return f"✓ 스킵: {os.path.basename(image_path)} (이미 {original_size:.1f}KB)"

            return f"✓ {os.path.basename(image_path)}: {original_size:.1f}KB → {final_size:.1f}KB (-{reduction:.1f}%){resolution_info}"

        except Exception as e:
            return f"✗ 실패: {os.path.basename(image_path)} - {str(e)}"

    def compress_video(self, video_path, max_height=1080):
        """동영상을 압축 (ffmpeg 사용)"""
        try:
            # 출력 파일 경로 (원본 폴더에 prefix를 붙여 저장)
            original_path = Path(video_path)
            output_filename = self.OUTPUT_PREFIX + original_path.name
            output_path = str(original_path.parent / output_filename)

            # ffmpeg가 설치되어 있는지 확인
            result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True)
            if result.returncode != 0:
                return f"✗ ffmpeg가 설치되지 않았습니다. 'brew install ffmpeg'로 설치하세요."

            original_size = os.path.getsize(video_path) / (1024 * 1024)

            # ffmpeg로 동영상 압축 (해상도 제한 포함)
            # -vf scale=-2:높이 : 비율 유지하며 높이 제한, -2는 짝수로 맞춤
            cmd = [
                'ffmpeg', '-i', video_path,
                '-vf', f'scale=-2:min({max_height}\\,ih)',  # 높이가 max_height보다 크면 축소
                '-vcodec', 'libx264',
                '-crf', '28',
                '-preset', 'fast',
                '-acodec', 'aac',  # 오디오 코덱
                '-b:a', '128k',  # 오디오 비트레이트
                '-y',  # 덮어쓰기
                output_path
            ]

            subprocess.run(cmd, capture_output=True, check=True)

            final_size = os.path.getsize(output_path) / (1024 * 1024)
            reduction = ((original_size - final_size) / original_size) * 100

            return f"✓ {os.path.basename(video_path)}: {original_size:.1f}MB → {final_size:.1f}MB (-{reduction:.1f}%)"

        except subprocess.CalledProcessError as e:
            return f"✗ 실패: {os.path.basename(video_path)} - ffmpeg 오류"
        except Exception as e:
            return f"✗ 실패: {os.path.basename(video_path)} - {str(e)}"

    def get_media_files(self, folder):
        """폴더에서 이미지와 동영상 파일 찾기"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.heic', '.heif'}
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}

        media_files = {'images': [], 'videos': []}

        if self.recursive.get():
            for root, dirs, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    ext = Path(file).suffix.lower()

                    if ext in image_extensions:
                        media_files['images'].append(file_path)
                    elif ext in video_extensions:
                        media_files['videos'].append(file_path)
        else:
            for file in os.listdir(folder):
                file_path = os.path.join(folder, file)
                if os.path.isfile(file_path):
                    ext = Path(file).suffix.lower()

                    if ext in image_extensions:
                        media_files['images'].append(file_path)
                    elif ext in video_extensions:
                        media_files['videos'].append(file_path)

        return media_files

    def process_files(self):
        folder = self.folder_path.get()

        if not folder or not os.path.isdir(folder):
            messagebox.showerror("오류", "올바른 폴더를 선택해주세요.")
            return

        self.start_button.config(state=tk.DISABLED)
        self.log_text.delete(1.0, tk.END)

        try:
            self.log("파일 검색 중...")
            media_files = self.get_media_files(folder)

            total_files = len(media_files['images']) + len(media_files['videos'])

            if total_files == 0:
                self.log("처리할 미디어 파일이 없습니다.")
                messagebox.showinfo("알림", "처리할 미디어 파일이 없습니다.")
                return

            self.log(f"\n찾은 파일: 이미지 {len(media_files['images'])}개, 동영상 {len(media_files['videos'])}개\n")

            processed = 0

            # 이미지 압축
            if media_files['images']:
                self.log("=== 이미지 압축 시작 ===")
                if not HEIC_SUPPORTED:
                    self.log("⚠ HEIC 파일 지원 안 됨 (pillow-heif 미설치)")
                for img_path in media_files['images']:
                    result = self.compress_image(img_path, self.target_size.get(), self.max_resolution.get())
                    self.log(result)
                    processed += 1
                    self.progress['value'] = (processed / total_files) * 100
                    self.root.update()

            # 동영상 압축
            if media_files['videos']:
                self.log("\n=== 동영상 압축 시작 ===")
                for video_path in media_files['videos']:
                    result = self.compress_video(video_path, self.max_video_height.get())
                    self.log(result)
                    processed += 1
                    self.progress['value'] = (processed / total_files) * 100
                    self.root.update()

            self.log("\n완료!")
            messagebox.showinfo("완료", f"총 {total_files}개 파일 처리 완료!")

        except Exception as e:
            messagebox.showerror("오류", f"처리 중 오류 발생: {str(e)}")
        finally:
            self.start_button.config(state=tk.NORMAL)
            self.progress['value'] = 0

    def start_compression(self):
        # 별도 스레드에서 실행하여 UI가 멈추지 않도록
        thread = threading.Thread(target=self.process_files)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = MediaCompressor(root)
    root.mainloop()
