import cv2
import matplotlib.pyplot as plt
import IPython.display as display
from IPython.display import clear_output
import mediapipe as mp
import time
import serial

def move_servos(pan, tilt):
    command = f'P{pan}T{tilt}\n'
    arduino.write(command.encode())

arduino = serial.Serial('COM9', 9600)  # Change 'COM3' to your Arduino's port

cap=cv2.VideoCapture(0)
mp_holistics=mp.solutions.holistic
mp_drawings=mp.solutions.drawing_utils
holistic=mp_holistics.Holistic(min_detection_confidence=0.5,min_tracking_confidence=0.5)
center_x = cap.get(cv2.CAP_PROP_FRAME_WIDTH) // 2
center_y = cap.get(cv2.CAP_PROP_FRAME_HEIGHT) // 2

# Servo movement calibration values (adjust based on your servos)
servo_pan_offset = 90  # Offset for centering pan servo
servo_tilt_offset = 65  # Offset for centering tilt servo
servo_pan_range = 180  # Pan servo movement range (degrees)
servo_tilt_range = 180  # Tilt servo movement range (degrees)
pan_movement_factor = 0.05 # Factor for scaling pan movement based on face offset
tilt_movement_factor = 0.05  # Factor for scaling tilt movement based on face offset
prevTime = 0

with mp_holistics.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        flip_image=cv2.flip(frame,1)
        image = cv2.cvtColor(flip_image, cv2.COLOR_BGR2RGB)
        results = holistic.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.circle(image, (int(center_x), int(center_y)), 5, (255, 0, 0), 2)
        # cv2.putText(image,f"{center_x,center_y}",(int(center_x), int(center_y)),cv2.FONT_HERSHEY_PLAIN, 1, (0, 196, 255), 1)  # Blue dot at the center of the frame
        if results.face_landmarks:
            h, w, _ = image.shape
            face_landmarks = results.face_landmarks.landmark
            x_min = min([lm.x for lm in face_landmarks]) * w
            x_max = max([lm.x for lm in face_landmarks]) * w
            y_min = min([lm.y for lm in face_landmarks]) * h
            y_max = max([lm.y for lm in face_landmarks]) * h
            cv2.circle(image, (int(x_min), int(y_min)), 5, (255, 0, 0), 2)
            # cv2.putText(image,f"{x_min,y_min}",(int(x_min), int(y_min)),cv2.FONT_HERSHEY_PLAIN, 1, (0, 196, 255), 1)
            cv2.circle(image, (int(x_max), int(y_max)), 5, (255, 0, 0), 2)
            # cv2.putText(image,f"{x_max,y_max}",(int(x_max), int(y_max)),cv2.FONT_HERSHEY_PLAIN, 1, (0, 196, 255), 1)
            face_center_x = (x_min + x_max) // 2.0
            face_center_y = (y_min + y_max) // 2.0
            # print(f"face coordinates: {face_center_x, face_center_y}")
            cv2.circle(image, (int(face_center_x),int(face_center_y)), 5, (0, 255, 0), 2)
            # cv2.putText(image,f"{face_center_x, face_center_y}",(int(face_center_x), int(face_center_y)),cv2.FONT_HERSHEY_PLAIN, 1, (0, 196, 255), 1)
            # Calculate offsets from center
            pan_offset = face_center_x - center_x
            tilt_offset = face_center_y - center_y
            # print(f"offsets: {pan_offset, tilt_offset}")

            # Scale offsets for servo movement
            pan_movement = int(pan_offset * pan_movement_factor)
            tilt_movement = int(tilt_offset * tilt_movement_factor)
            # print(f"servo movements: {pan_movement, tilt_movement}")

            # Apply offsets with calibration and clamp within servo range
            pan_position = servo_pan_offset + pan_movement
            tilt_position = servo_tilt_offset + tilt_movement  # Tilt often needs inversion
            # print(f"servo positions: {pan_position, tilt_position}")

            pan_position = max(0, min(pan_position, servo_pan_range))
            tilt_position = max(0, min(tilt_position, servo_tilt_range))
            print(f"clameped servo positions: {pan_position, tilt_position}")

            cv2.rectangle(image, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)
              # Green dot at the center of the face
            # Draw offset lines from the center of the frame to the center of the face
            cv2.line(image, (int(center_x), int(center_y)), (int(face_center_x), int(face_center_y)), (0, 0, 255), 2) 
            move_servos(int(pan_position*0.79), int(tilt_position*0.79))

        cv2.imshow("Live face Tracking",image)
        key=cv2.waitKey(1)
        if key & 0xFF==ord('q'):
            break

cap.release()
cv2.destroyAllWindows()