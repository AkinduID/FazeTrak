import cv2 # OpenCV for frame processing
import mediapipe as mp # MediaPipe library for Face and Gesture detection
import time # Time library for time tracking
import serial # Serial library for communication with Arduino
import pyvirtualcam
from simple_pid import PID

arduino = serial.Serial('COM9', 9600) # Change 'COM9' to your Arduino's port
cap = cv2.VideoCapture(0) # Set up video capture
mp_holistics = mp.solutions.holistic # Initialize MediaPipe Holistic model
mp_drawings = mp.solutions.drawing_utils # MediaPipe drawing utility
mp_hands = mp.solutions.hands # Initialize MediaPipe Hands model
frame_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
center_x = cap.get(cv2.CAP_PROP_FRAME_WIDTH) // 2 # Get the center of the frame
center_y = cap.get(cv2.CAP_PROP_FRAME_HEIGHT) // 2 # Get the center of the frame
vcam = pyvirtualcam.Camera(width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), fps=30)
# pan_pid = PID(1.0, 0.0, 0.1, setpoint=center_x)  # Adjust Kp, Ki, Kd as needed
# tilt_pid = PID(1.0, 0.0, 0.1, setpoint=center_y)
face_detector = mp_holistics.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
hand_detector = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# pan_angle = 90 # Offset for centering pan servo
# tilt_angle = 65 # Offset for centering tilt servo
# # Pan servo movement range (degrees)
# pan_max = 180 
# tilt_max = 180
# pan_min = 0
# tilt_min = 0
# step = 7 # Step size for servo movement
tolerance = 7 # Tolerance for face tracking
face_detected = False # Flag for face detection
face_locked = False # Flag for face locking

last_face_detect_time = time.time() # Time of last face detection
timeout = 5 # Timeout for face tracking

# PID variables
# Kp = 0.02  # Proportional gain
# Ki = 0.001  # Integral gain
# Kd = 0.05 # Derivative gain

# Initialize PID state variables
# integral_pan = 0
# integral_tilt = 0
# previous_error_pan = 0
# previous_error_tilt = 0

# def track_face_pid(face_center_x, face_center_y):
#     global pan_angle, tilt_angle
#     global integral_pan, integral_tilt, previous_error_pan, previous_error_tilt
    
#     # Calculate the error from the center positions
#     pan_error = abs(center_x - face_center_x)
#     tilt_error = abs(center_y - face_center_y)

#     # Calculate the integral term
#     integral_pan += pan_error
#     integral_pan = max(-10, min(10, integral_pan))
#     integral_tilt += tilt_error
#     integral_tilt = max(-10, min(10, integral_tilt))

#     # Calculate the derivative term
#     derivative_pan = pan_error - previous_error_pan
#     derivative_tilt = tilt_error - previous_error_tilt

#     # Calculate PID output
#     pan_output = Kp * pan_error + Ki * integral_pan + Kd * derivative_pan
#     tilt_output = Kp * tilt_error + Ki * integral_tilt + Kd * derivative_tilt

#     # Update previous error
#     previous_error_pan = pan_error
#     previous_error_tilt = tilt_error

#     if face_center_x < center_x - tolerance:
#         # pan_angle -= horizontal_step  # Move left min 0
#         pan_angle = max(pan_min, min(pan_max, int(pan_angle-pan_output)))
#     elif face_center_x > center_x + tolerance:
#         # pan_angle += horizontal_step  # Move right max 180
#         pan_angle = max(pan_min, min(pan_max, int(pan_angle+pan_output)))

#     # Tilt servo control (vertical)
#     if face_center_y < center_y - tolerance:
#         # tilt_angle -= vertical_step  # Move up min 0
#         tilt_angle = max(tilt_min, min(tilt_max, int(tilt_angle-tilt_output)))
#     elif face_center_y > center_y + tolerance:
#         # tilt_angle += vertical_step  # Move down max 180
#         tilt_angle = max(tilt_min, min(tilt_max, int(tilt_angle+tilt_output)))

#     # Constrain the outputs to a specific range, e.g., 0-180 degrees
#     # pan_angle = max(pan_min, min(pan_max, int(pan_angle+pan_output)))
#     # tilt_angle = max(tilt_min, min(tilt_max, int(tilt_angle+tilt_output)))

#     # Send angles to Arduino
#     move_servos(pan_angle, tilt_angle)
#     print(f"Face Center: ({face_center_x}, {face_center_y}), Pan Angle: {pan_angle}, Tilt Angle: {tilt_angle}, Pan Error: {pan_error}, Tilt Error: {tilt_error}")


def detect_hand_gesture(hand_landmarks):
    """Detects if the hand is showing an open palm (lock) or fist (unlock)."""
    if hand_landmarks:
        thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y
        index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
        middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y
        ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y
        pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y

        # Open palm gesture (lock)
        if thumb_tip < index_tip and thumb_tip < middle_tip and thumb_tip < ring_tip and thumb_tip < pinky_tip:
            return "lock"
        # Closed fist gesture (unlock)
        elif index_tip < thumb_tip and middle_tip < thumb_tip and ring_tip < thumb_tip and pinky_tip < thumb_tip:
            return "unlock"
    return None

# def move_servos(pan, tilt):
#     command = f'P{pan}T{tilt}\n'
#     arduino.write(command.encode())

def reset_servos():
    # global pan_angle, tilt_angle
    # pan_angle = 90  # Reset pan servo to center position
    # tilt_angle = 65  # Reset tilt servo to center position
    # move_servos(pan_angle, tilt_angle)
    command = f'RESET\n'
    arduino.write(command.encode())

# def track_face(face_center_x, face_center_y):
#     global pan_angle, tilt_angle

#     # Calculate distance from center
#     horizontal_distance = abs(face_center_x - center_x)
#     vertical_distance = abs(face_center_y - center_y)

#     # Determine step size based on distance (larger distance = larger step size)
#     horizontal_step = max(1, int((horizontal_distance / center_x) * step))
#     vertical_step = max(1, int((vertical_distance / center_y) * step))
 
#     # Pan servo control (horizontal)
#     if face_center_x < center_x - tolerance:
#         pan_angle -= horizontal_step  # Move left
#     elif face_center_x > center_x + tolerance:
#         pan_angle += horizontal_step  # Move right

#     # Tilt servo control (vertical)
#     if face_center_y < center_y - tolerance:
#         tilt_angle -= vertical_step  # Move up
#     elif face_center_y > center_y + tolerance:
#         tilt_angle += vertical_step  # Move down

#     # Constrain angles to servo limits
#     pan_angle = max(pan_min, min(pan_max, pan_angle))
#     tilt_angle = max(tilt_min, min(tilt_max, tilt_angle))

#     # Send angles to Arduino
#     move_servos(pan_angle, tilt_angle)

def move_servo2(face_center_x,face_center_y):
        # Pan servo control (horizontal)
    if face_center_x < center_x - tolerance:
        # pan_angle -= horizontal_step  # Move left
        command = f'P{face_center_x}T{face_center_y}L\n' # L for left
        arduino.write(command.encode())
    elif face_center_x > center_x + tolerance:
        # pan_angle += horizontal_step  # Move right
        command = f'P{face_center_x}T{face_center_y}R\n' # R for Right
        arduino.write(command.encode())
    # Tilt servo control (vertical)
    if face_center_y < center_y - tolerance:
        # tilt_angle -= vertical_step  # Move up
        command = f'P{face_center_x}T{face_center_y}U\n' # U for up
        arduino.write(command.encode())
    elif face_center_y > center_y + tolerance:
        # tilt_angle += vertical_step  # Move down
        command = f'P{face_center_x}T{face_center_y}D\n' # D for down
        arduino.write(command.encode())

def process_video():
    global last_face_detect_time, timeout, face_detected, face_locked, face_detector, hand_detector, vcam
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        flip_image=cv2.flip(frame,1)
        image_rgb = cv2.cvtColor(flip_image, cv2.COLOR_BGR2RGB)
        face_results = face_detector.process(image_rgb)
        hand_results = hand_detector.process(image_rgb)
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        cv2.circle(image_bgr, (int(center_x), int(center_y)), 5, (255, 0, 0), -1)
        cv2.line(image_bgr, (int(center_x), 0), (int(center_x), int(frame_height)), (255,0,0), 2)
        cv2.line(image_bgr, (0,int(center_y)), (int(frame_width), int(center_y)), (255,0,0), 2)
        cv2.circle(image_bgr,(0,0),5,(255, 0, 0), -1)
        if face_results.face_landmarks:
            face_detected = True
            last_face_detect_time = time.time()
            h, w, _ = image_rgb.shape
            face_landmarks = face_results.face_landmarks.landmark
            x_min = min([lm.x for lm in face_landmarks]) * w
            x_max = max([lm.x for lm in face_landmarks]) * w
            y_min = min([lm.y for lm in face_landmarks]) * h
            y_max = max([lm.y for lm in face_landmarks]) * h
            cv2.circle(image_bgr, (int(x_min), int(y_min)), 5, (255, 0, 0), -1)

            face_center_x = (x_min + x_max) // 2.0
            face_center_y = (y_min + y_max) // 2.0
            cv2.circle(image_bgr, (int(face_center_x),int(face_center_y)), 5, (0, 255, 0), -1)
            cv2.rectangle(image_bgr, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)
            cv2.line(image_bgr,(int(center_x),int(center_y)),(int(face_center_x),int(face_center_y)),(0,255,0),2)
            if face_locked:
                # track_face_pid(face_center_x, face_center_y)
                move_servo2(face_center_x,face_center_y)
        else:
            face_detected=False
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                mp_drawings.draw_landmarks(image_bgr, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                gesture = detect_hand_gesture(hand_landmarks)
                if gesture == "lock":
                    face_locked = True
                elif gesture == "unlock":
                    face_locked = False
        if not face_detected and (time.time() - last_face_detect_time > timeout):
            reset_servos()
            face_locked=False

        vcam.send(image_rgb)
        vcam.sleep_until_next_frame()

        cv2.imshow("Live face Tracking",image_bgr)
        key=cv2.waitKey(1)
        if key & 0xFF==ord('q'):
            reset_servos()
            break

    cap.release()
    cv2.destroyAllWindows()
    face_detector.close()
    hand_detector.close()
    vcam.close()

process_video()

    
