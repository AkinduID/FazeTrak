from PyQt5.QtCore import QThread, pyqtSignal as Signal
from PyQt5.QtGui import QImage
import cv2
import mediapipe as mp
import time
import pyvirtualcam
from gesture import detect_hand_gesture
from servo_controller import ServoController
import logging


# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VideoThread(QThread):
    frame_signal = Signal(QImage)

    def __init__(self):
        super().__init__()
        logger.info("Initializing VideoThread")
        self.cap = cv2.VideoCapture(1)
        logger.info(f"Camera opened: {self.cap.isOpened()}")
        
        self.vcam = pyvirtualcam.Camera(width=int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), height=int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), fps=30)
        logger.info("Virtual camera initialized")
        
        self.face_detector = mp.solutions.holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.hand_detector = mp.solutions.hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        logger.info("MediaPipe detectors initialized")
        
        self.running = True
        self.center_x = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) // 2
        self.center_y = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) // 2
        self.step = 7
        self.tolerance = 50
        self.face_locked = False
        self.last_face_detect_time = time.time()
        self.timeout = 5
        self.servo_controller = ServoController()
        logger.info("VideoThread initialization complete")
        
        # Performance tracking
        self.frame_count = 0
        self.last_log_time = time.time()

    def run(self):
        logger.info("VideoThread started running")
        while self.running and self.cap.isOpened():
            loop_start = time.time()
            
            ret, frame = self.cap.read()
            if not ret:
                logger.warning("Failed to read frame from camera")
                break
            
            read_time = time.time()
            logger.debug(f"Frame read time: {(read_time - loop_start) * 1000:.2f}ms")
            
            flip_image = cv2.flip(frame, 1)
            image_rgb = cv2.cvtColor(flip_image, cv2.COLOR_BGR2RGB)
            
            preprocess_time = time.time()
            logger.debug(f"Preprocessing time: {(preprocess_time - read_time) * 1000:.2f}ms")
            
            # Face detection
            face_results = self.face_detector.process(image_rgb)
            face_detect_time = time.time()
            logger.debug(f"Face detection time: {(face_detect_time - preprocess_time) * 1000:.2f}ms")
            
            # Hand detection
            hand_results = self.hand_detector.process(image_rgb)
            hand_detect_time = time.time()
            logger.debug(f"Hand detection time: {(hand_detect_time - face_detect_time) * 1000:.2f}ms")
            
            cv2.circle(image_rgb, (int(self.center_x), int(self.center_y)), 5, (255, 0, 0), 2)

            if face_results.face_landmarks:
                logger.debug("Face detected")
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
                    logger.debug("Tracking face (locked)")
                    track_start = time.time()
                    self.track_face(face_center_x, face_center_y)
                    track_time = time.time()
                    logger.debug(f"Face tracking time: {(track_time - track_start) * 1000:.2f}ms")
            else:
                if time.time() - self.last_face_detect_time > self.timeout:
                    logger.info("Face timeout - resetting servos")
                    self.servo_controller.reset_servos()
                    self.face_locked = False

            if hand_results.multi_hand_landmarks:
                logger.debug(f"Hand detected: {len(hand_results.multi_hand_landmarks)} hand(s)")
                for hand_landmarks in hand_results.multi_hand_landmarks:
                    gesture_start = time.time()
                    mp.solutions.drawing_utils.draw_landmarks(image_rgb, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)
                    gesture = detect_hand_gesture(hand_landmarks)
                    gesture_time = time.time()
                    logger.debug(f"Gesture detection time: {(gesture_time - gesture_start) * 1000:.2f}ms")
                    
                    if gesture == "lock":
                        logger.info("LOCK gesture detected - face tracking enabled")
                        self.face_locked = True
                    elif gesture == "unlock":
                        logger.info("UNLOCK gesture detected - face tracking disabled")
                        self.face_locked = False
                    elif gesture:
                        logger.debug(f"Other gesture detected: {gesture}")

            # Virtual camera
            try:
                vcam_start = time.time()
                self.vcam.send(image_rgb)
                vcam_time = time.time()
                logger.debug(f"Virtual camera send time: {(vcam_time - vcam_start) * 1000:.2f}ms")
            except Exception as e:
                logger.error(f"Virtual camera error: {e}")

            # Emit frame to GUI
            emit_start = time.time()
            h, w, ch = image_rgb.shape
            bytes_per_line = ch * w
            q_img = QImage(image_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.frame_signal.emit(q_img)
            emit_time = time.time()
            logger.debug(f"Frame emit time: {(emit_time - emit_start) * 1000:.2f}ms")
            
            # Overall loop timing
            loop_end = time.time()
            total_time = (loop_end - loop_start) * 1000
            logger.info(f"Total loop time: {total_time:.2f}ms ({1000/total_time:.1f} FPS)")
            
            self.frame_count += 1
            
            # Log summary every 30 frames
            if self.frame_count % 30 == 0:
                elapsed = time.time() - self.last_log_time
                avg_fps = 30 / elapsed
                logger.info(f"=== Frame {self.frame_count}: Average FPS: {avg_fps:.1f} ===")
                self.last_log_time = time.time()

    def track_face(self, face_center_x, face_center_y):
        logger.debug(f"Tracking face at ({face_center_x:.0f}, {face_center_y:.0f})")
        horizontal_distance = abs(face_center_x - self.center_x)
        vertical_distance = abs(face_center_y - self.center_y)
        horizontal_step = max(1, int((horizontal_distance / self.center_x) * self.step))
        vertical_step = max(1, int((vertical_distance / self.center_y) * self.step))

        old_pan = self.servo_controller.pan_angle
        old_tilt = self.servo_controller.tilt_angle

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
        
        if old_pan != self.servo_controller.pan_angle or old_tilt != self.servo_controller.tilt_angle:
            logger.debug(f"Servo move: Pan {old_pan}->{self.servo_controller.pan_angle}, Tilt {old_tilt}->{self.servo_controller.tilt_angle}")
            servo_start = time.time()
            self.servo_controller.move_servos(self.servo_controller.pan_angle, self.servo_controller.tilt_angle)
            servo_time = time.time()
            logger.debug(f"Servo command time: {(servo_time - servo_start) * 1000:.2f}ms")

    def close(self):
        logger.info("Closing VideoThread")
        self.running = False
        self.cap.release()
        self.vcam.close()
        self.face_detector.close()
        self.hand_detector.close()
        logger.info("VideoThread closed")