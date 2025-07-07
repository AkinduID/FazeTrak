# Face Tracking Desktop Application

This is a PyQt-based desktop application for face and hand gesture tracking using a webcam. It leverages OpenCV, MediaPipe, and PyVirtualCam to process video, detect faces and gestures, and (optionally) control servos for camera movement.

## Project Structure

- `app/` - Main application package
  - `main.py` - Application entry point and main window
  - `video_thread.py` - Video processing and threading logic
  - `gesture.py` - Hand gesture detection logic
  - `servo_controller.py` - Servo control logic
  - `resources/` - Images, icons, and other assets
- `README.md` - This file

## How to Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python -m app.main
   ```

## Features
- Real-time face and hand gesture detection
- Virtual webcam output
- Servo control logic (optional, for hardware integration)
- Modular, maintainable codebase 