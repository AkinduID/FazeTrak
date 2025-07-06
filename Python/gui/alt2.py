import cv2
import mediapipe as mp
import pyvirtualcam
import serial
import time
import threading
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QThread, pyqtSignal
from queue import Queue
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FaceGestureDetector:
    def __init__(self):
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.hands = mp.solutions.hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_results = self.face_mesh.process(rgb_frame)
        hand_results = self.hands.process(rgb_frame)
        return face_results, hand_results

    def close(self):
        self.face_mesh.close()
        self.hands.close()

class ServoController:
    def __init__(self, port="COM3", baud_rate=9600):
        self.port = port
        self.baud_rate = baud_rate
        self.arduino = None
        self.connect_arduino()

    def connect_arduino(self):
        try:
            self.arduino = serial.Serial(self.port, self.baud_rate, timeout=1)
            logging.info(f"Connected to Arduino on {self.port}")
        except serial.SerialException as e:
            logging.error(f"Failed to connect to Arduino: {e}")

    def move_servos(self, pan, tilt):
        if self.arduino and self.arduino.is_open:
            try:
                command = f"{pan},{tilt}\n"
                self.arduino.write(command.encode())
                logging.debug(f"Sent to Arduino: {command}")
            except Exception as e:
                logging.error(f"Error sending command to Arduino: {e}")

    def close(self):
        if self.arduino:
            self.arduino.close()
            logging.info("Arduino connection closed.")

class VideoThread(QThread):
    frame_processed = pyqtSignal(object)
    def __init__(self, detector, servo_controller):
        super().__init__()
        self.detector = detector
        self.servo_controller = servo_controller
        self.running = True
        self.frame_queue = Queue(maxsize=5)

    def run(self):
        cap = cv2.VideoCapture(0)
        with pyvirtualcam.Camera(width=640, height=480, fps=30) as cam:
            while self.running:
                if not cap.isOpened():
                    logging.error("Failed to open camera.")
                    break

                ret, frame = cap.read()
                if not ret:
                    logging.warning("Failed to read frame from camera.")
                    continue

                face_results, hand_results = self.detector.process_frame(frame)
                self.frame_processed.emit((frame, face_results, hand_results))
                
                # Process servo movement based on detection results
                if face_results and face_results.multi_face_landmarks:
                    face = face_results.multi_face_landmarks[0]
                    pan, tilt = self.calculate_servo_angles(face)
                    self.servo_controller.move_servos(pan, tilt)

                # Show frame in the virtual camera
                cam.send(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                cam.sleep_until_next_frame()

        cap.release()

    def calculate_servo_angles(self, face):
        # Dummy implementation for servo angle calculation
        # Add your logic based on face landmarks here
        pan = 90
        tilt = 90
        return pan, tilt

    def stop(self):
        self.running = False

class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.detector = FaceGestureDetector()
        self.servo_controller = ServoController()
        self.video_thread = VideoThread(self.detector, self.servo_controller)
        self.video_thread.frame_processed.connect(self.update_frame)

        self.init_ui()
        self.video_thread.start()

    def init_ui(self):
        self.setWindowTitle("Face Tracking System")
        self.setGeometry(100, 100, 800, 600)
        self.video_label = QtWidgets.QLabel(self)
        self.video_label.setGeometry(50, 50, 640, 480)

    def update_frame(self, data):
        frame, face_results, hand_results = data
        # Display the frame in the GUI
        qt_img = self.convert_cv_to_qt(frame)
        self.video_label.setPixmap(qt_img)

    def convert_cv_to_qt(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_img = QtGui.QImage(rgb_frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        return QtGui.QPixmap.fromImage(qt_img)

    def closeEvent(self, event):
        self.video_thread.stop()
        self.video_thread.wait()
        self.detector.close()
        self.servo_controller.close()
        super().closeEvent(event)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())
