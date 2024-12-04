# Face Tracking Webcam Project

## Project Overview
EyeRiz is a smart webcam capable of face recognition, gesture-based face locking, tracking, and release the lock, developed For the CS3283 - Embedded Systems Project in Semester 5. The system includes a standard consumer webcam, two servo motors mounted on a servo bracket for pan-tilt control, a microcontroller, LED indicators, and a custom desktop application. The app processes the video stream for face and gesture detection, calculates servo angles to center the face, and communicates with the microcontroller via serial. Servo Motors get the angles from the microcontroller and move the webcam which is also mounted on the servo bracket. Using the OBS Virtual Camera driver, the app streams the tracked video feed to other applications like Zoom while keeping the original feed locked to the desktop app.

## Features
- Real-time face detection and tracking
- Locking and Unlocking a face using hand gestures
- Desktop Application for further features

## Technologies and Tools
<a href="https://www.python.org/">
        <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" height="30" alt="python logo" />
</a>
 <a href="https://isocpp.org/">
        <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/cplusplus/cplusplus-original.svg" height="30" alt="cplusplus logo" />
      </a>
<a href="https://wiki.python.org/moin/PyQt">
        <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/qt/qt-original.svg" height="30" alt="qt logo" />
      </a>
<a href="https://opencv.org/">
        <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/opencv/opencv-original.svg" height="30" alt="opencv logo" />
      </a>
  <a href="https://ai.google.dev/edge/mediapipe/framework">
        <img src="https://viz.mediapipe.dev/logo.png" height="30" alt="MediaPipe logo" />
      </a>
 <a href="https://code.visualstudio.com/">
        <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/vscode/vscode-original.svg" height="30" alt="vscode logo" />
      </a>
<a href="https://www.arduino.cc/">
        <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/arduino/arduino-original.svg" height="30" alt="arduino logo" />
      </a>
      <a href="https://platformio.org/">
        <img src="https://cdn.platformio.org/images/platformio-logo.17fdc3bc.png" height="30" alt="platformio logo" />
      </a>
  
## Hardware Compnents
- 720p Web Camera
- Arduino Uno R3
- SG90 Servo Motors x2
- Pan and Tilt Servo Bracket
  
## Read the wiki for the weekly progress
https://github.com/AkinduID/Face-Tracking-WebCam/wiki
