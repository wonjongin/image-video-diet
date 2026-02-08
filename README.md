# Image & Video Diet

A simple yet powerful desktop application for batch compressing images and videos. Reduce file sizes while maintaining acceptable quality with an intuitive GUI.

## Features

- **Image Compression**
  - Supports multiple formats: JPG, PNG, GIF, BMP, WebP, TIFF, HEIC/HEIF
  - Automatic resolution resizing
  - Target file size control
  - Quality optimization with iterative compression
  - Automatic RGBA to RGB conversion for JPEG compatibility

- **Video Compression**
  - Supports formats: MP4, AVI, MOV, MKV, WMV, FLV, WebM
  - Resolution scaling with aspect ratio preservation
  - H.264 video encoding with AAC audio
  - Configurable maximum height

- **Batch Processing**
  - Process entire folders at once
  - Optional recursive subfolder scanning
  - Real-time progress tracking
  - Detailed compression statistics

## Screenshot

![Application Screenshot](imgs/screenshot.png)

## Requirements

- Python 3.8+
- FFmpeg (for video compression)
  - **Windows**: FFmpeg binary should be placed in `bin/ffmpeg.exe`
  - **macOS/Linux**: System FFmpeg installation

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/image-video-diet.git
cd image-video-diet
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install FFmpeg:
   - **Windows**: Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html) and place `ffmpeg.exe` in the `bin/` directory
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt-get install ffmpeg` or equivalent

## Usage

### Running from Source

```bash
python media_compressor.py
```

### Building an Executable

For Windows:
```powershell
.\build.ps1
```

The executable will be created in the `dist/` directory.

### Using the Application

1. **Select Folder**: Click "찾아보기" (Browse) to choose a folder containing your media files
2. **Configure Options**:
   - **Image Target Size (KB)**: Desired file size for compressed images (default: 200 KB)
   - **Image Max Resolution (px)**: Maximum dimension for images (default: 1024 px)
   - **Video Max Height (px)**: Maximum video height in pixels (default: 480 px)
   - **Include Subfolders**: Enable to process files in subdirectories
3. **Start Compression**: Click "압축 시작" (Start Compression)
4. **Monitor Progress**: View real-time logs and progress bar

Compressed files are saved in the same directory as the originals with the prefix `압축_` (compressed_).

## Configuration

Default settings can be modified in the GUI:

| Setting | Default | Description |
|---------|---------|-------------|
| Image Target Size | 200 KB | Target file size for compressed images |
| Image Max Resolution | 1024 px | Maximum dimension (width or height) |
| Video Max Height | 480 px | Maximum video height |
| Include Subfolders | ✓ | Process files recursively |

## Technical Details

- **Image Compression**: Uses Pillow (PIL) with LANCZOS resampling and iterative quality adjustment
- **Video Compression**: Uses FFmpeg with libx264 codec, CRF 28, and 128k AAC audio
- **HEIC Support**: Optional support via pillow-heif library
- **Threading**: Asynchronous processing to prevent UI freezing

## File Format Support

### Images
`.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`, `.tiff`, `.heic`, `.heif`

### Videos
`.mp4`, `.avi`, `.mov`, `.mkv`, `.wmv`, `.flv`, `.webm`

## Output

Compressed files are named with the prefix `압축_` followed by the original filename:
- Original: `photo.jpg` → Compressed: `압축_photo.jpg`
- Original: `video.mp4` → Compressed: `압축_video.mp4`

## License

This project is open source and available under the [MIT License](LICENSE).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Built with [Pillow](https://python-pillow.org/) for image processing
- [FFmpeg](https://ffmpeg.org/) for video compression
- [pillow-heif](https://github.com/bigcat88/pillow_heif) for HEIC support
