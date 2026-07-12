# FazeTrak

<div align="left">

<a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white"/></a>
<a href="https://isocpp.org/"><img src="https://img.shields.io/badge/C++-00599C?style=flat&logo=c%2B%2B&logoColor=white"/></a>
<a href="https://www.qt.io/"><img src="https://img.shields.io/badge/PyQt-41CD52?style=flat&logo=qt&logoColor=white"/></a>
<a href="https://www.espressif.com/en/products/socs/esp32"><img src="https://img.shields.io/badge/ESP32-000000?style=flat&logo=espressif&logoColor=white"/></a>
<a href="https://platformio.org/"><img src="https://img.shields.io/badge/PlatformIO-FF7F32?style=flat&logo=platformio&logoColor=white"/></a>
<a href="https://code.visualstudio.com/"><img src="https://custom-icon-badges.demolab.com/badge/Visual%20Studio%20Code-0078d7.svg?logo=visualstudiocode&logoColor=white"/></a>
<a href="https://opencv.org/"><img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=flat&logo=opencv&logoColor=white"/></a>
<a href="https://mediapipe.dev/"><img src="https://img.shields.io/badge/MediaPipe-2196F3?style=flat&logo=google&logoColor=white"/></a>

**Smart face-tracking webcam system with gesture control and ESP32-C3 servo integration**

<img src="https://github.com/AkinduID/FazeTrak/blob/main/assets/fazetrak.jpg"/>

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
- [Documentation](#documentation)
- [Contributing](#contributing)


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
- ✅ **Virtual Camera Support** - Stream to OBS, Zoom, Teams
- ✅ **Desktop Application** - Full PyQt5 GUI with live preview

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
│   │    parameters
│   ├── requirements.txt
│   └── README.md
├── device-firmware/
│   ├── src/
│   │   └── main.cpp                # ESP32-C3 servo control firmware
│   ├── platformio.ini
│   └── README.md
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
- Python 3.10
- PyQt5
- OpenCV (cv2)
- MediaPipe
- pyvirtualcam
- OBS Virtual Camera Plugin

### ESP32-C3 Firmware
- PlatformIO
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
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download OBS Studio**
https://obsproject.com/download

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
  - ✋ **Open Palm** → Release face lock
  - ✊ **Closed Fist** → Lock face and start tracking

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


