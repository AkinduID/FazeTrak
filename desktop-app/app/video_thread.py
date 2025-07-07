from PyQt5.QtCore import QThread, pyqtSignal as Signal
from PyQt5.QtGui import QImage
import cv2
import mediapipe as mp
import time
import pyvirtualcam
from gesture import detect_hand_gesture
from servo_controller import ServoController

class VideoThread(QThread):
    frame_signal = Signal(QImage)

    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)
        self.vcam = pyvirtualcam.Camera(width=int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), height=int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), fps=30)
        self.face_detector = mp.solutions.holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.hand_detector = mp.solutions.hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.running = True
        self.center_x = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) // 2
        self.center_y = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) // 2
        self.step = 7
        self.tolerance = 50
        self.face_locked = False
        self.last_face_detect_time = time.time()
        self.timeout = 5
        self.servo_controller = ServoController()

    def run(self):
        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            flip_image = cv2.flip(frame, 1)
            image_rgb = cv2.cvtColor(flip_image, cv2.COLOR_BGR2RGB)
            face_results = self.face_detector.process(image_rgb)
            hand_results = self.hand_detector.process(image_rgb)
            cv2.circle(image_rgb, (int(self.center_x), int(self.center_y)), 5, (255, 0, 0), 2)

            if face_results.face_landmarks:
                self.last_face_detect_time = time.time()
                h, w, _ = image_rgb.shape
                face_landmarks = face_results.face_landmarks.landmark
                x_min = min([lm.x for lm in face_landmarks]) * w
                x_max = max([lm.x for lm in face_landmarks]) * w
                y_min = min([lm.y for lm in face_landmarks]) * h
                y_max = max([lm.y for lm in face_landmarks]) * h
                face_center_x = (x_min + x_max) // 2
                face_center_y = (y_min + y_max) // 2

                cv2.circle(image_rgb, (int(face_center_x), int(face_center_y)), 5, (0, 255, 0), 2)
                cv2.rectangle(image_rgb, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)
                cv2.line(image_rgb, (int(self.center_x), int(self.center_y)), (int(face_center_x), int(face_center_y)), (0, 255, 0), 2)

                if self.face_locked:
                    self.track_face(face_center_x, face_center_y)
            else:
                if time.time() - self.last_face_detect_time > self.timeout:
                    self.servo_controller.reset_servos()
                    self.face_locked = False

            if hand_results.multi_hand_landmarks:
                for hand_landmarks in hand_results.multi_hand_landmarks:
                    mp.solutions.drawing_utils.draw_landmarks(image_rgb, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)
                    gesture = detect_hand_gesture(hand_landmarks)
                    if gesture == "lock":
                        self.face_locked = True
                    elif gesture == "unlock":
                        self.face_locked = False

            self.vcam.send(image_rgb)
            self.vcam.sleep_until_next_frame()

            h, w, ch = image_rgb.shape
            bytes_per_line = ch * w
            q_img = QImage(image_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.frame_signal.emit(q_img)

    def track_face(self, face_center_x, face_center_y):
        horizontal_distance = abs(face_center_x - self.center_x)
        vertical_distance = abs(face_center_y - self.center_y)
        horizontal_step = max(1, int((horizontal_distance / self.center_x) * self.step))
        vertical_step = max(1, int((vertical_distance / self.center_y) * self.step))

        if face_center_x < self.center_x - self.tolerance:
            self.servo_controller.pan_angle -= horizontal_step
        elif face_center_x > self.center_x + self.tolerance:
            self.servo_controller.pan_angle += horizontal_step

        if face_center_y < self.center_y - self.tolerance:
            self.servo_controller.tilt_angle -= vertical_step
        elif face_center_y > self.center_y + self.tolerance:
            self.servo_controller.tilt_angle += vertical_step

        self.servo_controller.pan_angle = max(0, min(180, self.servo_controller.pan_angle))
        self.servo_controller.tilt_angle = max(0, min(180, self.servo_controller.tilt_angle))
        self.servo_controller.move_servos(self.servo_controller.pan_angle, self.servo_controller.tilt_angle)

    def close(self):
        self.running = False
        self.cap.release()
        self.vcam.close()
        self.face_detector.close()
        self.hand_detector.close() 