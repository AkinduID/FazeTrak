import cv2 as cv
import matplotlib.pyplot as plt
import IPython.display as display
from IPython.display import clear_output
import mediapipe as mp
import time
cap=cv.VideoCapture(0)
mp_holistics=mp.solutions.holistic
mp_drawings=mp.solutions.drawing_utils
holistic=mp_holistics.Holistic(min_detection_confidence=0.5,min_tracking_confidence=0.5)

with mp_holistics.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        image = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        results = holistic.process(image)
        image = cv.cvtColor(image, cv.COLOR_RGB2BGR)
        if results.face_landmarks:
            h, w, _ = image.shape
            face_landmarks = results.face_landmarks.landmark
            x_min = min([lm.x for lm in face_landmarks]) * w
            x_max = max([lm.x for lm in face_landmarks]) * w
            y_min = min([lm.y for lm in face_landmarks]) * h
            y_max = max([lm.y for lm in face_landmarks]) * h
            cv.rectangle(image, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)
        cv.imshow("Live face Tracking",image)
        key=cv.waitKey(1)
        if key & 0xFF==ord('q'):
            break

cap.release()
cv.destroyAllWindows()