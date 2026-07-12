"""
Background thread that owns the webcam capture loop: it reads frames, runs
face/hand detection, applies gesture-based lock/unlock control, drives the
pan/tilt servos toward a detected face, mirrors the annotated frame to a
virtual camera, and emits each frame to the GUI for display.

Running this on a QThread keeps the potentially slow per-frame work (camera
I/O, MediaPipe inference, serial writes) off the Qt GUI event loop so the
window stays responsive.
"""

import logging
import time
from typing import Optional

import cv2
import mediapipe as mp
import pyvirtualcam
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage

from fazetrak import config
from fazetrak.hardware.servo_controller import ServoController
from fazetrak.vision.face_tracker import FaceTracker, ServoAngles
from fazetrak.vision.gesture_recognizer import Gesture, recognize_gesture

logger = logging.getLogger(__name__)


class VideoProcessingThread(QThread):
    """
    Captures webcam frames and processes them for face/gesture tracking.

    Emits:
        frame_ready(QImage): a new annotated frame, ready to be displayed.
    """

    frame_ready = pyqtSignal(QImage)

    def __init__(self, servo_controller: ServoController) -> None:
        super().__init__()
        logger.info("Initializing video processing thread.")

        self.servo_controller = servo_controller
        self._is_running = False
        self._tracking_locked = False
        self._last_face_seen_at = time.time()
        self._processed_frame_count = 0
        self._last_fps_log_time = time.time()

        self._camera = self._open_camera()
        frame_width, frame_height = self._get_frame_dimensions(self._camera)

        self._virtual_camera = self._open_virtual_camera(frame_width, frame_height)
        self._face_detector = mp.solutions.holistic.Holistic(
            min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE,
        )
        self._hand_detector = mp.solutions.hands.Hands(
            min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE,
        )
        self._face_tracker = FaceTracker(frame_width, frame_height)

        logger.info("Video processing thread initialized (%dx%d).", frame_width, frame_height)

    # -- Setup helpers --------------------------------------------------------

    @staticmethod
    def _open_camera() -> cv2.VideoCapture:
        """Open the configured webcam and log whether it succeeded."""
        camera = cv2.VideoCapture(config.CAMERA_INDEX)
        logger.info("Camera %d opened: %s", config.CAMERA_INDEX, camera.isOpened())
        return camera

    @staticmethod
    def _get_frame_dimensions(camera: cv2.VideoCapture) -> tuple[int, int]:
        width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return width, height

    @staticmethod
    def _open_virtual_camera(width: int, height: int) -> pyvirtualcam.Camera:
        virtual_camera = pyvirtualcam.Camera(
            width=width, height=height, fps=config.VIRTUAL_CAMERA_FPS
        )
        logger.info("Virtual camera initialized (%dx%d).", width, height)
        return virtual_camera

    # -- Main loop --------------------------------------------------------------

    def run(self) -> None:
        """Entry point invoked by QThread.start(); runs until stop() is called."""
        logger.info("Video processing loop started.")
        self._is_running = True

        while self._is_running and self._camera.isOpened():
            frame = self._read_next_frame()
            if frame is None:
                break

            annotated_frame = self._process_frame(frame)
            self._publish_to_virtual_camera(annotated_frame)
            self._emit_frame_to_gui(annotated_frame)
            self._log_frame_rate()

        logger.info("Video processing loop exited.")

    def stop(self) -> None:
        """Signal the loop to stop and release all camera/model resources."""
        logger.info("Stopping video processing thread.")
        self._is_running = False
        self._camera.release()
        self._virtual_camera.close()
        self._face_detector.close()
        self._hand_detector.close()
        logger.info("Video processing thread stopped and resources released.")

    def set_tracking_locked(self, locked: bool) -> None:
        """Enable or disable active face tracking (servo correction)."""
        self._tracking_locked = locked
        logger.info("Face tracking %s.", "locked" if locked else "unlocked")

    # -- Per-frame processing --------------------------------------------------

    def _read_next_frame(self):
        """Read one frame from the webcam, mirrored for a natural selfie view."""
        frame_read_ok, frame = self._camera.read()
        if not frame_read_ok:
            logger.warning("Failed to read frame from camera; stopping loop.")
            return None
        return cv2.flip(frame, 1)

    def _process_frame(self, frame):
        """Run detection, gesture handling, and tracking on a single frame."""
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self._draw_frame_center_marker(image_rgb)

        face_results = self._face_detector.process(image_rgb)
        hand_results = self._hand_detector.process(image_rgb)

        self._handle_face_detection(face_results, image_rgb)
        self._handle_hand_gestures(hand_results, image_rgb)

        return image_rgb

    def _draw_frame_center_marker(self, image_rgb) -> None:
        """Draw a marker at the frame's center, used as the tracking target."""
        cv2.circle(
            image_rgb,
            (self._face_tracker.frame_center_x, self._face_tracker.frame_center_y),
            5,
            (255, 0, 0),
            2,
        )

    def _handle_face_detection(self, face_results, image_rgb) -> None:
        """Annotate the detected face and, if locked, correct the servos toward it."""
        if not face_results.face_landmarks:
            self._handle_no_face_detected()
            return

        self._last_face_seen_at = time.time()
        face_center_x, face_center_y = self._draw_face_bounding_box(face_results, image_rgb)

        if self._tracking_locked:
            self._track_face(face_center_x, face_center_y)

    def _handle_no_face_detected(self) -> None:
        """If tracking is locked and the face has been lost too long, recenter."""
        seconds_since_last_face = time.time() - self._last_face_seen_at
        if seconds_since_last_face > config.FACE_LOST_TIMEOUT_SECONDS:
            logger.info("No face detected for %.1fs; recentering servos.", seconds_since_last_face)
            self.servo_controller.reset_to_default_position()
            self._tracking_locked = False

    def _draw_face_bounding_box(self, face_results, image_rgb) -> tuple[float, float]:
        """Draw the detected face's bounding box and return its center point."""
        frame_height, frame_width, _ = image_rgb.shape
        landmarks = face_results.face_landmarks.landmark

        x_min = min(landmark.x for landmark in landmarks) * frame_width
        x_max = max(landmark.x for landmark in landmarks) * frame_width
        y_min = min(landmark.y for landmark in landmarks) * frame_height
        y_max = max(landmark.y for landmark in landmarks) * frame_height
        face_center_x = (x_min + x_max) // 2
        face_center_y = (y_min + y_max) // 2

        cv2.circle(image_rgb, (int(face_center_x), int(face_center_y)), 5, (0, 255, 0), 2)
        cv2.rectangle(
            image_rgb, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2
        )
        cv2.line(
            image_rgb,
            (self._face_tracker.frame_center_x, self._face_tracker.frame_center_y),
            (int(face_center_x), int(face_center_y)),
            (0, 255, 0),
            2,
        )
        return face_center_x, face_center_y

    def _track_face(self, face_center_x: float, face_center_y: float) -> None:
        """Compute and apply a servo correction to recenter the given face position."""
        current_angles = ServoAngles(
            pan_degrees=self.servo_controller.pan_angle_degrees,
            tilt_degrees=self.servo_controller.tilt_angle_degrees,
        )
        new_angles = self._face_tracker.compute_correction(
            face_center_x, face_center_y, current_angles
        )
        if new_angles != current_angles:
            self.servo_controller.move_to(new_angles.pan_degrees, new_angles.tilt_degrees)

    def _handle_hand_gestures(self, hand_results, image_rgb) -> None:
        """Detect lock/unlock gestures in any visible hands and act on them."""
        if not hand_results.multi_hand_landmarks:
            return

        logger.debug("Hands detected: %d", len(hand_results.multi_hand_landmarks))
        for hand_landmarks in hand_results.multi_hand_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(
                image_rgb, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS
            )
            gesture = recognize_gesture(hand_landmarks)
            self._apply_gesture(gesture)

    def _apply_gesture(self, gesture: Optional[Gesture]) -> None:
        """Update tracking lock state based on a recognized gesture, if any."""
        if gesture == Gesture.LOCK and not self._tracking_locked:
            logger.info("LOCK gesture detected; face tracking enabled.")
            self.set_tracking_locked(True)
        elif gesture == Gesture.UNLOCK and self._tracking_locked:
            logger.info("UNLOCK gesture detected; face tracking disabled.")
            self.set_tracking_locked(False)

    # -- Output -----------------------------------------------------------------

    def _publish_to_virtual_camera(self, image_rgb) -> None:
        """Send the annotated frame to the virtual camera output, if possible."""
        try:
            self._virtual_camera.send(image_rgb)
        except Exception:
            logger.exception("Failed to send frame to virtual camera.")

    def _emit_frame_to_gui(self, image_rgb) -> None:
        """Convert the frame to a QImage and emit it for display in the GUI."""
        frame_height, frame_width, channel_count = image_rgb.shape
        bytes_per_line = channel_count * frame_width
        qt_image = QImage(
            image_rgb.data, frame_width, frame_height, bytes_per_line, QImage.Format_RGB888
        )
        # QImage does not copy the underlying buffer by default; since
        # image_rgb is a local variable about to go out of scope, force a
        # deep copy so the emitted image remains valid on the GUI thread.
        self.frame_ready.emit(qt_image.copy())

    def _log_frame_rate(self) -> None:
        """Periodically log the average frame rate for basic performance visibility."""
        self._processed_frame_count += 1
        if self._processed_frame_count % 30 == 0:
            elapsed_seconds = time.time() - self._last_fps_log_time
            average_fps = 30 / elapsed_seconds if elapsed_seconds > 0 else 0.0
            logger.info(
                "Processed %d frames (avg %.1f fps over last 30).",
                self._processed_frame_count,
                average_fps,
            )
            self._last_fps_log_time = time.time()
