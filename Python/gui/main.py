from PyQt5 import QtWidgets
from PyQt5.QtGui import QImage,QPixmap
from PyQt5.QtCore import QThread,pyqtSignal as Signal,pyqtSlot as Slot
import imutils
import sys
import cv2 
import mediapipe as mp 
import time
import serial
import pyvirtualcam

class VideoThread(QThread):
    frame_signal = Signal(QImage)

    def __init__(self):
        super().__init__()
        self.cap=cv2.VideoCapture(0)
        self.vcam = pyvirtualcam.Camera(width=int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), height=int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), fps=30)
        self.face_detector = mp.solutions.holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.hand_detector = mp.solutions.hands.Hands(min_detection_confidence=0.5,min_tracking_confidence=0.5)
        # self.mp_drawings = mp.solutions.drawing_utils
        # self.arduino = serial.Serial("COM9",9600)
        self.running = True
        self.center_x = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) // 2
        self.center_y = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) // 2
        self.pan_angle = 90
        self.tilt_angle = 65
        self.step = 7
        self.tolerance = 50
        self.face_locked = False
        self.last_face_detect_time = time.time()
        self.timeout = 5

    def run(self):
        while self.running and self.cap.isOpened():
            ret,frame = self.cap.read()
            if not ret:
                break
            flip_image = cv2.flip(frame, 1)
            image_rgb = cv2.cvtColor(flip_image, cv2.COLOR_BGR2RGB)
            face_results = self.face_detector.process(image_rgb)
            hand_results = self.hand_detector.process(image_rgb)
            # image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
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
                    self.reset_servos()
                    self.face_locked = False

            if hand_results.multi_hand_landmarks:
                for hand_landmarks in hand_results.multi_hand_landmarks:
                    mp.solutions.drawing_utils.draw_landmarks(image_rgb, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)
                    gesture = self.detect_hand_gesture(hand_landmarks)
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

    #         frame = self.cvimage_to_label(frame)
    #         self.frame_signal.emit(frame)
    
    # def cvimage_to_label(self,image):
    #     image = imutils.resize(image,width = 640)
    #     image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
    #     image = QImage(image,image.shape[1],image.shape[0],QImage.Format_RGB888)
    #     return image
    
    def detect_hand_gesture(self, hand_landmarks):
        """Detects if the hand is showing an open palm (lock) or fist (unlock)."""
        if hand_landmarks:
            thumb_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP].y
            index_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP].y
            middle_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP].y
            ring_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_TIP].y
            pinky_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_TIP].y

            if thumb_tip < index_tip and thumb_tip < middle_tip and thumb_tip < ring_tip and thumb_tip < pinky_tip:
                return "lock"
            elif index_tip < thumb_tip and middle_tip < thumb_tip and ring_tip < thumb_tip and pinky_tip < thumb_tip:
                return "unlock"
        return None
    
    def track_face(self, face_center_x, face_center_y):
        horizontal_distance = abs(face_center_x - self.center_x)
        vertical_distance = abs(face_center_y - self.center_y)
        horizontal_step = max(1, int((horizontal_distance / self.center_x) * self.step))
        vertical_step = max(1, int((vertical_distance / self.center_y) * self.step))

        if face_center_x < self.center_x - self.tolerance:
            self.pan_angle -= horizontal_step
        elif face_center_x > self.center_x + self.tolerance:
            self.pan_angle += horizontal_step

        if face_center_y < self.center_y - self.tolerance:
            self.tilt_angle -= vertical_step
        elif face_center_y > self.center_y + self.tolerance:
            self.tilt_angle += vertical_step

        self.pan_angle = max(0, min(180, self.pan_angle))
        self.tilt_angle = max(0, min(180, self.tilt_angle))
        self.move_servos(self.pan_angle, self.tilt_angle)

    def move_servos(self, pan, tilt):
        command = f'P{pan}T{tilt}\n'
        # self.arduino.write(command.encode())

    def reset_servos(self):
        self.pan_angle = 90
        self.tilt_angle = 65
        self.move_servos(self.pan_angle, self.tilt_angle)

    def close(self):
        self.running = False
        self.cap.release()
        self.vcam.close()
        self.face_detector.close()
        self.hand_detector.close()

class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Tracking Application")
        self.setFixedSize(800, 600)

        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(20, 60, 760, 520)

        self.start_btn = QtWidgets.QPushButton("Start Tracking", self)
        self.start_btn.setGeometry(20, 20, 120, 30)
        self.start_btn.clicked.connect(self.start_tracking)

        self.stop_btn = QtWidgets.QPushButton("Stop Tracking", self)
        self.stop_btn.setGeometry(160, 20, 120, 30)
        self.stop_btn.clicked.connect(self.stop_tracking)

        self.video_thread = VideoThread()
        self.video_thread.frame_signal.connect(self.update_frame)

    @Slot(QImage)
    def update_frame(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    def start_tracking(self):
        if not self.video_thread.isRunning():
            self.video_thread.start()

    def stop_tracking(self):
        self.video_thread.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec())