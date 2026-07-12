"""
Centralized configuration for FazeTrak.

Keeping every tunable value in one place makes the behavior of the
application easy to adjust without hunting through business logic, and
makes the intent of each "magic number" explicit via its variable name.
"""

# --- Camera / video capture -------------------------------------------------

# Index of the physical webcam to read from (as passed to cv2.VideoCapture).
CAMERA_INDEX: int = 0

# Frames per second requested from the virtual camera output.
VIRTUAL_CAMERA_FPS: int = 30


# --- MediaPipe detection thresholds -----------------------------------------

MIN_DETECTION_CONFIDENCE: float = 0.5
MIN_TRACKING_CONFIDENCE: float = 0.5


# --- Face tracking behaviour -------------------------------------------------

# How many degrees the servos move per correction step at maximum.
TRACKING_STEP_DEGREES: int = 7

# How far (in pixels) the detected face can drift from the frame center
# before the tracker starts correcting for it. Prevents constant jitter.
TRACKING_TOLERANCE_PIXELS: int = 50

# If no face has been detected for this many seconds while tracking is
# "locked", the servos are recentered and locking is released.
FACE_LOST_TIMEOUT_SECONDS: float = 5.0


# --- Servo defaults ----------------------------------------------------------

DEFAULT_PAN_ANGLE_DEGREES: int = 90
DEFAULT_TILT_ANGLE_DEGREES: int = 65
MIN_SERVO_ANGLE_DEGREES: int = 0
MAX_SERVO_ANGLE_DEGREES: int = 180


# --- Arduino / serial connection --------------------------------------------

# USB hardware ID substring used to recognize the tracking rig's Arduino
# among all serial devices connected to the machine.
ARDUINO_USB_HWID: str = "303A:1001"

SERIAL_BAUD_RATE: int = 115200
SERIAL_READ_TIMEOUT_SECONDS: float = 0.01
SERIAL_WRITE_TIMEOUT_SECONDS: float = 0.01

# How often the GUI polls the servo controller to refresh the "Arduino
# connected" status label, in milliseconds.
ARDUINO_STATUS_POLL_INTERVAL_MS: int = 2000


# --- Main window -------------------------------------------------------------

WINDOW_TITLE: str = "FazeTrak"
WINDOW_WIDTH: int = 800
WINDOW_HEIGHT: int = 600

VIDEO_VIEW_X: int = 20
VIDEO_VIEW_Y: int = 60
VIDEO_VIEW_WIDTH: int = 760
VIDEO_VIEW_HEIGHT: int = 520


# --- Logging -----------------------------------------------------------------

LOG_DIRECTORY: str = "logs"
LOG_FILE_NAME: str = "fazetrak.log"
LOG_FORMAT: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
