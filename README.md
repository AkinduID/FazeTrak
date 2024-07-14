# Face Tracking Webcam Project

## Project Overview
This project aims to develop a face tracking webcam. The system will detect and track faces in real-time, providing a robust solution for applications requiring automated monitoring and human-computer interaction. This repository will document the entire development process, from initial planning to final implementation.

## Proposed Features
- Real-time face detection and tracking
- Locking and Unlocking a face using hand gestures
- Desktop Application for furhter features

## Proposed Technologies and Tools
- **Programming Languages**: Python, C/C++
- **Libraries**: OpenCV
- **Hardware**: Webcam
- **Development Environment**: VSCode,Arduino IDE

## Camera Options
### 1. Exsisting WebCam
The Basic Option is to use an exsisting webcam and convert it to a smart webcam. The webcam will be moounted on a pan and tilt servo bracket and the video feed will be captured by the desktop application and facial detection algorithms will run on the PC. The Desktop Application Can Control the Servo bracket via Arduino serial communication. This method is very cost effective since i already own a webcam (Logitech C270 HD). Project like this are already availible as tutorials. So if i choose this option i will focus more on the features of the desktop application and optimizing the servo movements.

### 2. AI-Thinker ESP32 Camera Development Board
The AI-Thinker ESP32 Camera Development Board is considered a compact, cost-effective solution for integrating camera functionalities with the ESP32 microcontroller. However, during testing, a significant issue was encountered: the microcontroller chip overheats quickly when the camera module is in use, causing all operations to slow down. Despite numerous tutorials and forum discussions on using this development board, none adequately address the overheating problem or provide effective fixes. Given that the board was purchased from a local store, there is a possibility it might be a cheap copy of the original. Further testing is required to either find a fix for this issue, identify a development board without this problem, or devise a method to cool down the chip.

### 3. OpenMV Camera Board
The OpenMV Camera Board is a powerful option, featuring an ARM Cortex M7 processor running at 400MHz. It allows for advanced image processing on the microcontroller itself and supports machine vision capabilities, running scripts written in MicroPython. This board is ideal for standalone applications where processing is done on the board, minimizing the need for constant communication with an external computer. Without budget constraints, this board is the ideal option for my project, as it enables the development of a truly embedded smart webcam.
However, availability and cost are major issues. This development board is not available in local stores, and its price ranges from 20,000 LKR to 40,000 LKR in foreign stores, with high shipping costs. The lowest shipping cost is listed on AliExpress, which can sometimes be an unreliable source. Given the high stakes associated with ordering from AliExpress, further research is required to determine a reliable and cost-effective way to obtain this board

### 4. Raspberry Pi Zero W/Raspberry Pi 4 Model B + Pi Camera
Using a Raspberry Pi (either the Zero W or Model 4) along with a Pi Camera offers a flexible and powerful solution for this project. The Raspberry Pi can handle image processing tasks and run Python scripts directly. However, I have several concerns regarding this option. While not as costly as the OpenMV Camera Board, this option still involves moderate costs. Borrowing a Raspberry Pi Model 4 is a potential solution. And Raspberry Pi boards are known to overheat when running computer vision applications.
Since I am developing this project as a universal webcam that can be plugged into any system, this option does not align well with that goal. Using a single-board computer (SBC) between the camera and the PC adds unnecessary complexity. Additionally, while this setup allows for the development of a more sophisticated Linux desktop application it essentially mirrors the first option but with a development environment in Linux rather than on the PC directly.

### 5. OV7670 Camera Module + Arduino/ESP32
The OV7670 Camera Module is an affordable option for integrating basic camera functionality with microcontrollers like Arduino or ESP32. However, this option has very limited processing power and image quality. The OV7670 will capture the video stream and send it to the PC desktop application via Arduino serial communication for object detection purposes. The application will also control the servo motor via Arduino serial communication.
The main concerns with this option are the limited image quality, processing power, and interfacing complexity. These limitations pose a higher risk of failure or degraded performance in the final implementation.
