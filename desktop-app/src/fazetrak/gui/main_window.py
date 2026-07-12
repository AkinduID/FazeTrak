"""
Main application window for FazeTrak.

Hosts the live video preview, tracking start/stop controls, and an Arduino
connection status indicator. Owns the ``VideoProcessingThread`` and the
``ServoController`` it depends on.
"""

import logging
from typing import Optional

from PyQt5.QtCore import QTimer, Qt, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel, QMainWindow, QPushButton

from fazetrak import config
from fazetrak.hardware.servo_controller import ServoController
from fazetrak.vision.video_processor import VideoProcessingThread

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Top-level application window tying together the UI and the video pipeline."""

    def __init__(self) -> None:
        super().__init__()

        # The video thread depends on a working camera + virtual camera
        # device, so it is created lazily on first "Start Tracking" click
        # rather than here, to avoid crashing the window on launch when
        # that hardware isn't available yet.
        self._video_thread: Optional[VideoProcessingThread] = None
        self._servo_controller = ServoController()

        self._configure_window()
        self._build_widgets()
        self._start_arduino_status_polling()

    # -- UI construction ---------------------------------------------------------

    def _configure_window(self) -> None:
        self.setWindowTitle(config.WINDOW_TITLE)
        self.setFixedSize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

    def _build_widgets(self) -> None:
        self._video_view = QLabel(self)
        self._video_view.setGeometry(
            config.VIDEO_VIEW_X,
            config.VIDEO_VIEW_Y,
            config.VIDEO_VIEW_WIDTH,
            config.VIDEO_VIEW_HEIGHT,
        )

        self._arduino_status_label = QLabel("Arduino Status: Not Connected", self)
        self._arduino_status_label.setGeometry(20, 580, 300, 20)

        self._start_button = QPushButton("Start Tracking", self)
        self._start_button.setGeometry(20, 20, 120, 30)
        self._start_button.clicked.connect(self._on_start_tracking_clicked)

        self._stop_button = QPushButton("Stop Tracking", self)
        self._stop_button.setGeometry(160, 20, 120, 30)
        self._stop_button.clicked.connect(self._on_stop_tracking_clicked)

    def _start_arduino_status_polling(self) -> None:
        self._arduino_poll_timer = QTimer(self)
        self._arduino_poll_timer.timeout.connect(self._refresh_arduino_status_label)
        self._arduino_poll_timer.start(config.ARDUINO_STATUS_POLL_INTERVAL_MS)

    # -- Button handlers ----------------------------------------------------------

    def _on_start_tracking_clicked(self) -> None:
        """Lazily create (or reuse) the video thread and start it."""
        if self._video_thread is None:
            try:
                self._video_thread = VideoProcessingThread(self._servo_controller)
            except Exception:
                # Most commonly: no webcam at config.CAMERA_INDEX, or no
                # virtual camera device (e.g. v4l2loopback) available.
                logger.exception("Failed to initialize the video pipeline.")
                self._arduino_status_label.setText(
                    "Video pipeline failed to start - see logs/fazetrak.log"
                )
                return
            self._video_thread.frame_ready.connect(self._on_frame_ready)

        if not self._video_thread.isRunning():
            logger.info("Start Tracking clicked; starting video thread.")
            self._video_thread.start()

    def _on_stop_tracking_clicked(self) -> None:
        """Stop the video thread if it is currently running."""
        if self._video_thread is not None and self._video_thread.isRunning():
            logger.info("Stop Tracking clicked; stopping video thread.")
            self._video_thread.stop()

    # -- Slots ----------------------------------------------------------------------

    @pyqtSlot(QImage)
    def _on_frame_ready(self, frame: QImage) -> None:
        """Display a newly processed frame in the video view, preserving aspect ratio."""
        pixmap = QPixmap.fromImage(frame)
        scaled_pixmap = pixmap.scaled(
            self._video_view.width(),
            self._video_view.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self._video_view.setPixmap(scaled_pixmap)

    def _refresh_arduino_status_label(self) -> None:
        """Update the Arduino status label based on the current connection state."""
        if self._servo_controller.is_connected():
            port_name = self._servo_controller.get_connected_port_name()
            self._arduino_status_label.setText(f"Arduino Status: Connected - {port_name}")
        else:
            self._arduino_status_label.setText("Arduino Status: Not Connected")

    # -- Lifecycle --------------------------------------------------------------------

    def closeEvent(self, event) -> None:  # noqa: N802 (Qt override signature)
        """Ensure the video thread is cleanly stopped when the window closes."""
        if self._video_thread is not None and self._video_thread.isRunning():
            self._video_thread.stop()
            self._video_thread.wait()
        super().closeEvent(event)
