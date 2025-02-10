# EyeRiz
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white"/></a>
<a href="https://isocpp.org/"><img src="https://img.shields.io/badge/C++-00599C?style=flat&logo=c%2B%2B&logoColor=white"/></a>
<a href="https://www.qt.io/"><img src="https://img.shields.io/badge/PyQt-41CD52?style=flat&logo=qt&logoColor=white"/></a>
<a href="https://www.arduino.cc/"><img src="https://img.shields.io/badge/Arduino-00979D?style=flat&logo=arduino&logoColor=white"/></a>
<a href="https://code.visualstudio.com/"><img src="https://img.shields.io/badge/VS%20Code-007ACC?style=flat&logo=visual-studio-code&logoColor=white"/></a></a>
<a href="https://opencv.org/"><img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=flat&logo=opencv&logoColor=white"/></a>
<a href="https://mediapipe.dev/"><img src="https://img.shields.io/badge/MediaPipe-2196F3?style=flat&logo=google&logoColor=white"/></a>

## Project Overview
EyeRiz is a smart webcam capable of face recognition, gesture-based face locking, tracking, and release the lock, developed For the CS3283 - Embedded Systems Project in Semester 5. The system includes a standard consumer webcam, two servo motors mounted on a servo bracket for pan-tilt control, a microcontroller, LED indicators, and a custom desktop application. The app processes the video stream for face and gesture detection, calculates servo angles to center the face, and communicates with the microcontroller via serial. Servo Motors get the angles from the microcontroller and move the webcam which is also mounted on the servo bracket. Using the OBS Virtual Camera driver, the app streams the tracked video feed to other applications like Zoom while keeping the original feed locked to the desktop app.

## Features
- Real-time face detection and tracking
- Locking and Unlocking a face using hand gestures
- Desktop Application for further features

  
## Read the wiki for the weekly progress
https://github.com/AkinduID/Face-Tracking-WebCam/wiki
