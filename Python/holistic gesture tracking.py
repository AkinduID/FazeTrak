import cv2
import mediapipe as mp
import time
import serial

# Initialize Arduino communication
arduino = serial.Serial('COM9', 9600)  # Change 'COM9' to your Arduino's port

# Initialize MediaPipe
mp_holistics = mp.solutions.holistic
mp_hands = mp.solutions.hands
mp_drawings = mp.solutions.drawing_utils
holistic = mp_holistics.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Set up video capture
cap = cv2.VideoCapture(0)
center_x = cap.get(cv2.CAP_PROP_FRAME_WIDTH) // 2
center_y = cap.get(cv2.CAP_PROP_FRAME_HEIGHT) // 2

# Servo movement calibration values
pan_angle = 90  # Offset for centering pan servo
tilt_angle = 65  # Offset for centering tilt servo
pan_max = 180  # Pan servo movement range (degrees)
tilt_max = 180  # Tilt servo movement range (degrees)
step = 8
tolerance = 50
pan_min = 0
tilt_min = 0

# Variables for locking mechanism
face_locked = False
locked_face_coords = None

def move_servos(pan, tilt):
    command = f'P{pan}T{tilt}\n'
    arduino.write(command.encode())

def track_face(face_center_x, face_center_y):
    global pan_angle, tilt_angle

    # Calculate distance from center
    horizontal_distance = abs(face_center_x - center_x)
    vertical_distance = abs(face_center_y - center_y)

    # Determine step size based on distance (larger distance = larger step size)
    horizontal_step = max(1, int((horizontal_distance / center_x) * step))
    vertical_step = max(1, int((vertical_distance / center_y) * step))

    # Pan servo control (horizontal)
    if face_center_x < center_x - tolerance:
        pan_angle -= horizontal_step  # Move left
    elif face_center_x > center_x + tolerance:
        pan_angle += horizontal_step  # Move right

    # Tilt servo control (vertical)
    if face_center_y < center_y - tolerance:
        tilt_angle -= vertical_step  # Move up
    elif face_center_y > center_y + tolerance:
        tilt_angle += vertical_step  # Move down

    # Constrain angles to servo limits
    pan_angle = max(pan_min, min(pan_max, pan_angle))
    tilt_angle = max(tilt_min, min(tilt_max, tilt_angle))

    # Send angles to Arduino
    move_servos(pan_angle, tilt_angle)

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

with mp_holistics.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic, mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        flip_image = cv2.flip(frame, 1)
        image = cv2.cvtColor(flip_image, cv2.COLOR_BGR2RGB)
        results = holistic.process(image)
        hand_results = hands.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.circle(image, (int(center_x), int(center_y)), 5, (255, 0, 0), 2)

        # Detect face and get its center coordinates
        if results.face_landmarks:
            h, w, _ = image.shape
            face_landmarks = results.face_landmarks.landmark
            x_min = min([lm.x for lm in face_landmarks]) * w
            x_max = max([lm.x for lm in face_landmarks]) * w
            y_min = min([lm.y for lm in face_landmarks]) * h
            y_max = max([lm.y for lm in face_landmarks]) * h
            face_center_x = (x_min + x_max) // 2.0
            face_center_y = (y_min + y_max) // 2.0

            cv2.circle(image, (int(face_center_x), int(face_center_y)), 5, (0, 255, 0), 2)
            cv2.rectangle(image, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)
            cv2.line(image, (int(center_x), int(center_y)), (int(face_center_x), int(face_center_y)), (0, 255, 0), 2)

            # Lock face if gesture detected
            if face_locked:
                # track_face(locked_face_coords[0], locked_face_coords[1])
                track_face(face_center_x, face_center_y)
            # else:
            #     track_face(face_center_x, face_center_y)
            #     locked_face_coords = (face_center_x, face_center_y)

        # Detect hand gestures for locking/unlocking
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                mp_drawings.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                gesture = detect_hand_gesture(hand_landmarks)
                if gesture == "lock":
                    face_locked = True
                    # locked_face_coords = (face_center_x, face_center_y)
                elif gesture == "unlock":
                    face_locked = False

        cv2.imshow("Live Face Tracking", image)
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
