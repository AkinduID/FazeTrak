from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import pyqtSlot as Slot, QTimer
import sys
from video_thread import VideoThread

class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FazeTrak")
        self.setFixedSize(800, 600)

        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(20, 60, 760, 520)

        self.arduino_status = QtWidgets.QLabel("Arduino Status: Not Connected", self)
        self.arduino_status.setGeometry(20, 580, 300, 20)

        self.start_btn = QtWidgets.QPushButton("Start Tracking", self)
        self.start_btn.setGeometry(20, 20, 120, 30)
        self.start_btn.clicked.connect(self.start_tracking)

        self.stop_btn = QtWidgets.QPushButton("Stop Tracking", self)
        self.stop_btn.setGeometry(160, 20, 120, 30)
        self.stop_btn.clicked.connect(self.stop_tracking)

        self.video_thread = VideoThread()
        self.video_thread.frame_signal.connect(self.update_frame)

        # QTimer to check Arduino connection
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_arduino_connection)
        self.timer.start(2000)  # Check every 2 seconds

    @Slot(QImage)
    def update_frame(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    def start_tracking(self):
        if not self.video_thread.isRunning():
            self.video_thread.start()

    def stop_tracking(self):
        self.video_thread.close()

    def check_arduino_connection(self):
        servo_controller = self.video_thread.servo_controller
        if servo_controller.is_connected():
            self.arduino_status.setText(f"Arduino Status: Connected - {servo_controller.get_port()}")
        else:
            self.arduino_status.setText("Arduino Status: Not Connected")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec()) 