import cv2
import serial
import time
import imutils

# Initialize serial communication with Arduino
arduino = serial.Serial('COM9', 9600)  # Change 'COM3' to your Arduino's port
time.sleep(2)  # Give some time for the connection to establish

# Face detection classifier (Haar Cascade)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Camera setup
cap = cv2.VideoCapture(0)

# Servo movement parameters
pan_angle = 90  # Initial angle for pan servo (horizontal)
tilt_angle = 90  # Initial angle for tilt servo (vertical)
pan_max = 180
pan_min = 0
tilt_max = 180
tilt_min = 0
step = 5  # How much to move the servo in each step

# Camera resolution (for face tracking)
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
center_x = frame_width // 2
center_y = frame_height // 2
tolerance = 50  # Tolerance for centering the face

def move_servos(pan, tilt):
    command = f'P{pan}T{tilt}\n'
    arduino.write(command.encode())

# Function to move servos based on face position
def track_face(x, y, w, h):
    global pan_angle, tilt_angle

    face_center_x = x + w // 2
    face_center_y = y + h // 2

    # Pan servo control (horizontal)
    if face_center_x < center_x - tolerance:
        pan_angle += step
    elif face_center_x > center_x + tolerance:
        pan_angle -= step

    # Tilt servo control (vertical)
    if face_center_y < center_y - tolerance:
        tilt_angle += step
    elif face_center_y > center_y + tolerance:
        tilt_angle -= step

    # Constrain angles to servo limits
    pan_angle = max(pan_min, min(pan_max, pan_angle))
    tilt_angle = max(tilt_min, min(tilt_max, tilt_angle))

    # Send angles to Arduino
    move_servos(tilt_angle, pan_angle)

while True:
    ret, frame = cap.read()
    #  frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)

    for (x, y, w, h) in faces:
        # Draw rectangle around the face
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        # Track face position and move servos
        track_face(x, y, w, h)

    # Display the frame
    cv2.imshow('Face Tracking', frame)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
cap.release()
cv2.destroyAllWindows()
arduino.close()
