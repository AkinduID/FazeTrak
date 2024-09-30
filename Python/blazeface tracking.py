import cv2
import mediapipe as mp
import time
import serial  # Import serial library for communication with microcontroller

# Microcontroller serial communication settings
# Adjust these based on your setup

# arduino = serial.Serial('COM9', 9600)  # Change 'COM3' to your Arduino's port

# Face detection and drawing utilities
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# Capture video from webcam
cap = cv2.VideoCapture(0)

# Camera image center coordinates (assuming a known image resolution)
center_x = cap.get(cv2.CAP_PROP_FRAME_WIDTH) // 2
center_y = cap.get(cv2.CAP_PROP_FRAME_HEIGHT) // 2

# Servo movement calibration values (adjust based on your servos)
servo_pan_offset = 0  # Offset for centering pan servo
servo_tilt_offset = 0  # Offset for centering tilt servo
servo_pan_range = 180  # Pan servo movement range (degrees)
servo_tilt_range = 180  # Tilt servo movement range (degrees)
pan_movement_factor = 0.2  # Factor for scaling pan movement based on face offset
tilt_movement_factor = 0.2  # Factor for scaling tilt movement based on face offset

prevTime = 0
with mp_face_detection.FaceDetection(
    min_detection_confidence=0.5
) as face_detection:
    while True:
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            break

        # Convert BGR to RGB for MediaPipe processing
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = face_detection.process(image)

        # Draw detection annotations on the image
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.detections:
            for detection in results.detections:
                # Get face bounding box center coordinates
                box_x_min = int(detection.location_data.relative_bounding_box.xmin * image.shape[1])
                box_y_min = int(detection.location_data.relative_bounding_box.ymin * image.shape[0])
                box_width = int(detection.location_data.relative_bounding_box.width * image.shape[1])
                box_height = int(detection.location_data.relative_bounding_box.height * image.shape[0])
                face_center_x = box_x_min + box_width // 2
                face_center_y = box_y_min + box_height // 2

                # Calculate offsets from center
                pan_offset = face_center_x - center_x
                tilt_offset = face_center_y - center_y

                # Scale offsets for servo movement
                pan_movement = int(pan_offset * pan_movement_factor)
                tilt_movement = int(tilt_offset * tilt_movement_factor)

                # Apply offsets with calibration and clamp within servo range
                pan_position = servo_pan_offset + pan_movement
                tilt_position = servo_tilt_offset - tilt_movement  # Tilt often needs inversion

                pan_position = max(0, min(pan_position, servo_pan_range))
                tilt_position = max(0, min(tilt_position, servo_tilt_range))
                print(pan_position, tilt_position)

                # Send servo control commands (adjust format according to your microcontroller)
                # arduino.write(f"P{pan_position}\nT{tilt_position}\n".encode())

                # Draw bounding box and center point for visualization
                cv2.rectangle(image, (box_x_min, box_y_min), (box_x_min + box_width, box_y_min + box_height), (0, 255, 0), 2)
                cv2.circle(image, (face_center_x, face_center_y), 5, (0, 0, 255), -1)

        currTime = time.time()
        fps = 1 / (currTime - prevTime)
        prevTime = currTime
        cv2.putText(image, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 196, 255), 2)
        cv2.imshow('BlazeFace Face Detection', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
cap.release()
cv2.destroyAllWindows()
# arduino.close()