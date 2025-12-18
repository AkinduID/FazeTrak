# FazeTrak

<div align="center">

<a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white"/></a>
<a href="https://isocpp.org/"><img src="https://img.shields.io/badge/C++-00599C?style=flat&logo=c%2B%2B&logoColor=white"/></a>
<a href="https://www.qt.io/"><img src="https://img.shields.io/badge/PyQt-41CD52?style=flat&logo=qt&logoColor=white"/></a>
<a href="https://www.arduino.cc/"><img src="https://img.shields.io/badge/Arduino-00979D?style=flat&logo=arduino&logoColor=white"/></a>
<a href="https://platformio.org/"><img src="https://img.shields.io/badge/PlatformIO-FF7F32?style=flat&logo=platformio&logoColor=white"/></a>
<a href="https://code.visualstudio.com/"><img src="https://img.shields.io/badge/VS%20Code-007ACC?style=flat&logo=visual-studio-code&logoColor=white"/></a>
<a href="https://opencv.org/"><img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=flat&logo=opencv&logoColor=white"/></a>
<a href="https://mediapipe.dev/"><img src="https://img.shields.io/badge/MediaPipe-2196F3?style=flat&logo=google&logoColor=white"/></a>

**Smart face-tracking webcam system with gesture control and ESP32-C3 servo integration**

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Hardware Requirements](#hardware-requirements)
- [Software Requirements](#software-requirements)
- [Installation](#installation)
- [Usage](#usage)
- [System Architecture](#system-architecture)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

FazeTrak is an intelligent webcam system capable of real-time face detection, gesture-based control, and autonomous tracking. Developed for **CS3283 - Embedded Systems Project (Semester 5)**, the system combines computer vision, embedded systems, and robotics to create a self-centering camera platform.

The system uses:
- **Desktop Application** (PyQt5) - Face/gesture detection and servo control
- **ESP32-C3 Microcontroller** - Servo motor driver and command processing
- **Pan-Tilt Mechanism** - Dual servo motors for 2-axis tracking
- **Virtual Camera Integration** - Stream tracked video to Zoom, OBS, etc.

---

## ✨ Features

- ✅ **Real-time Face Detection** - Powered by MediaPipe
- ✅ **Gesture-based Control** - Lock/unlock tracking with hand gestures
- ✅ **Autonomous Tracking** - Servos automatically center face in frame
- ✅ **Kalman Filter State Estimation** - Smooth tracking with noise reduction
- ✅ **Virtual Camera Support** - Stream to OBS, Zoom, Teams
- ✅ **Desktop Application** - Full PyQt5 GUI with live preview
- ✅ **ESP32-C3 Integration** - Wireless-capable servo control
- ✅ **Configurable Parameters** - Easy tuning via `configs.py`

---

## 📁 Project Structure

```
Face-Tracking-WebCam/
├── desktop-app/
│   ├── app/
│   │   ├── main.py                 # PyQt5 GUI entry point
│   │   ├── video_thread.py         # Video capture & face tracking
│   │   ├── servo_controller.py     # Serial communication with ESP32-C3
│   │   ├── gesture.py              # Hand gesture detection
│   │   ├── kalman_filter.py        # 2D Kalman Filter for smoothing
│   │   └── configs.py              # Configuration parameters
│   ├── requirements.txt
│   └── README.md
├── device-firmware/
│   ├── src/
│   │   └── main.cpp                # ESP32-C3 servo control firmware
│   ├── platformio.ini
│   └── README.md
├── Python/
│   ├── component test files/
│   ├── model tests/
│   └── port.py                     # Serial port enumeration utility
├── assets/
│   ├── esp32_c3_supermini.jpeg
│   ├── circuit.png
│   └── ...
├── README.md
└── .gitignore
```

---

## 🔧 Hardware Requirements

- **Microcontroller**: ESP32-C3 SuperMini
- **Servos**: 2× SG90 Pan-Tilt Servos (180° range)
- **Webcam**: Logitech C270 HD (or compatible USB camera)
- **Servo Bracket**: Pan-Tilt mount
- **USB Cable**: Type-C (ESP32-C3 connection)
- **5V Power Supply**: For servo motors (optional external power)

### Hardware Connections

| ESP32-C3 Pin | Component |
|--------------|-----------|
| GPIO 4       | Pan Servo Signal |
| GPIO 3       | Tilt Servo Signal |
| GND          | Servo GND |
| 5V           | Servo VCC (via external PSU) |

---

## 💻 Software Requirements

### Desktop Application
- Python 3.8+
- PyQt5
- OpenCV (cv2)
- MediaPipe
- pyvirtualcam

### ESP32-C3 Firmware
- PlatformIO
- Arduino Framework
- ESP32Servo library

---

## 📦 Installation

### Desktop Application Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/AkinduID/FazeTrak.git
   cd FazeTrak/desktop-app
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### ESP32-C3 Firmware Setup

1. **Install PlatformIO**
   ```bash
   pip install platformio
   ```

2. **Navigate to firmware directory**
   ```bash
   cd device-firmware
   ```

3. **Build and upload**
   ```bash
   platformio run -t upload
   ```

---

## 🚀 Usage

### Starting the Desktop Application

```bash
cd desktop-app
python -m app.main
```

**Controls:**
- **Start Tracking** - Begin face detection and servo control
- **Stop Tracking** - Stop the tracking system
- **Hand Gestures**:
  - ✋ **Open Palm** → Lock face tracking
  - ✊ **Closed Fist** → Unlock face tracking

**Visual Feedback:**
- 🔵 **Blue circle** - Raw face detection (noisy)
- 🟡 **Yellow circle** - Kalman Filter estimate (smooth)
- 🟢 **Green rectangle** - Face bounding box
- 🟢 **Green line** - Servo aim vector

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────┐
│      Desktop Application (PyQt5)    │
├─────────────────────────────────────┤
│  ┌───────────────────────────────┐  │
│  │  Video Input (Webcam)         │  │
│  └──────────────┬────────────────┘  │
│                 │                    │
│  ┌──────────────▼────────────────┐  │
│  │  Face Detection (MediaPipe)   │  │
│  └──────────────┬────────────────┘  │
│                 │                    │
│  ┌──────────────▼────────────────┐  │
│  │  Kalman Filter (Smoothing)    │  │
│  └──────────────┬────────────────┘  │
│                 │                    │
│  ┌──────────────▼────────────────┐  │
│  │  Servo Control Algorithm      │  │
│  └──────────────┬────────────────┘  │
│                 │                    │
└─────────────────┼────────────────────┘
                  │ Serial @ 115200 baud
         ┌────────▼─────────┐
         │   ESP32-C3       │
         ├──────────────────┤
         │ Servo Driver     │
         │ (PWM Generator)  │
         └────────┬─────────┘
                  │
         ┌────────┴──────────┐
         │                   │
      ┌──▼──┐          ┌──▼──┐
      │ Pan │          │Tilt │
      │Servo│          │Servo│
      └─────┘          └─────┘
```

---

## ⚙️ Configuration

Edit `desktop-app/app/configs.py` to adjust:

```python
# Kalman Filter tuning
KF_PROCESS_NOISE = 0.01        # Process model trust (lower = more trust)
KF_MEASUREMENT_NOISE = 25      # Detection trust (lower = more trust)

# Servo control zones
SERVO_TOLERANCE = 80           # Dead zone in pixels
SERVO_STEP_SMALL = 1           # Close-range step size
SERVO_STEP_MEDIUM = 2          # Mid-range step size
SERVO_STEP_LARGE = 3           # Far-range step size
SERVO_ZONE_MEDIUM = 150        # Pixels threshold for medium step
SERVO_ZONE_LARGE = 250         # Pixels threshold for large step
SERVO_UPDATE_RATE = 2          # Update rate throttle (frames)
SERVO_PAN_CENTER = 90          # Pan home position
SERVO_TILT_CENTER = 65         # Tilt home position
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Servos don't move | Check serial connection, verify ESP32 firmware uploaded |
| Video freezes | Reduce detection confidence, increase frame skip |
| Overshooting | Decrease step sizes, increase `SERVO_TOLERANCE` |
| Hunting (oscillating) | Increase `SERVO_UPDATE_RATE`, widen tolerance zone |
| Virtual camera not showing | Install OBS Virtual Camera driver |
| Port detection fails | Run `python port.py` to list available COM ports |

---

## 📚 Documentation

For detailed progress and technical documentation, see:
- [GitHub Wiki](https://github.com/AkinduID/FazeTrak/wiki) - Weekly progress and technical details
- [Desktop App README](desktop-app/README.md)
- [Firmware README](device-firmware/README.md)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👥 Authors

- **Project Team** - CS3283 Embedded Systems, Semester 5

---

## 📞 Support & Questions

For questions or issues:
- Check the [Wiki](https://github.com/AkinduID/FazeTrak/wiki)
- Open an [Issue](https://github.com/AkinduID/FazeTrak/issues)
- Review this README

---

## 🎓 Acknowledgments

- **MediaPipe** - Face detection framework
- **OpenCV** - Computer vision library
- **PyQt5** - Desktop GUI framework
- **ESP32-C3** - Microcontroller platform
- **PlatformIO** - Embedded development

---

<div align="center">

**Made with ❤️ for CS3283 - Embedded Systems Project**

[⬆ back to top](#fazetrak)

</div>
