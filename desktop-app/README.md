# FazeTrak

A PyQt5 desktop application for webcam-based face and hand-gesture tracking.
It uses OpenCV and MediaPipe to detect a face and hand gestures, mirrors the
annotated video to a virtual camera, and (optionally) drives a pan/tilt servo
rig over serial to physically follow the detected face.

## How it works

- Show an **open palm** to lock tracking on; the servo rig will follow your
  face.
- Show a **closed fist** to unlock tracking.
- If your face isn't seen for a few seconds while locked, the rig recenters
  and unlocks automatically.
- The Arduino connection status is shown at the bottom of the window and
  refreshes automatically.

## Project structure

```
fazetrak/
├── run.py                       # Entry point: python run.py
├── requirements.txt
├── pyproject.toml               # Optional: `pip install -e .` for an installable package
├── src/
│   └── fazetrak/
│       ├── config.py            # All tunable constants in one place
│       ├── logging_config.py    # Console + rotating file logging setup
│       ├── gui/
│       │   └── main_window.py   # Qt main window, widgets, and event handlers
│       ├── vision/
│       │   ├── video_processor.py    # Camera capture + detection loop (QThread)
│       │   ├── face_tracker.py       # Pure pan/tilt correction math (unit-testable)
│       │   └── gesture_recognizer.py # Lock/unlock hand-gesture classification
│       └── hardware/
│           └── servo_controller.py   # Serial communication with the Arduino rig
└── logs/                         # Created automatically; rotating log files
```

Each layer only depends on the ones below it: `gui` depends on `vision` and
`hardware`; `vision` depends on `hardware` only through the `ServoController`
interface it's given; `hardware` and `face_tracker` have no GUI/camera
dependencies at all, which is what makes them straightforward to unit test.

### Architecture Data Flow

```mermaid
graph TB
    %% --- Color Definitions & Styles ---
    classDef external fill:#f9f7f1,stroke:#b5a67c,stroke-width:2px,stroke-dasharray: 5 5;
    classDef entry fill:#eef2ff,stroke:#4f46e5,stroke-width:2px;
    classDef gui fill:#ecfdf5,stroke:#059669,stroke-width:2px;
    classDef vision fill:#fff7ed,stroke:#ea580c,stroke-width:2px;
    classDef hardware fill:#fdf2f8,stroke:#db2777,stroke-width:2px;
    classDef cross fill:#f8fafc,stroke:#64748b,stroke-width:1px;

    %% --- Subgraphs ---
    subgraph External["External hardware"]
        Webcam[("Webcam")]
        VirtualCam[("Virtual camera output")]
        Arduino[("Arduino pan/tilt rig")]
    end

    subgraph GUILayer["gui/"]
        MainWindow["MainWindow<br/>widgets, event handlers"]
    end

    subgraph VisionLayer["vision/"]
        VideoProcessor["VideoProcessingThread<br/>capture + detection loop"]
        FaceTracker["FaceTracker<br/>pan/tilt correction math"]
        GestureRecognizer["gesture_recognizer<br/>lock/unlock classification"]
    end

    subgraph HardwareLayer["hardware/"]
        ServoController["ServoController<br/>serial communication"]
    end

    subgraph CrossCutting["cross-cutting"]
        Config["config.py"]
        Logging["logging_config.py"]
    end

    %% --- Core Components ---
    EntryPoint["run.py<br/>entry point"]

    %% --- Connections & Relationships ---
    EntryPoint --> MainWindow
    EntryPoint --> ServoController

    Webcam --> VideoProcessor
    MainWindow -->|"start / stop tracking"| VideoProcessor
    VideoProcessor -->|"frame_ready signal"| MainWindow
    VideoProcessor --> VirtualCam
    VideoProcessor --> GestureRecognizer
    VideoProcessor --> FaceTracker
    FaceTracker -->|"corrected angles"| VideoProcessor
    VideoProcessor -->|"move_to(pan, tilt)"| ServoController
    MainWindow -->|"poll connection status"| ServoController
    ServoController --> Arduino

    Config -.-> MainWindow
    Config -.-> VideoProcessor
    Config -.-> FaceTracker
    Config -.-> ServoController
    Logging -.-> MainWindow
    Logging -.-> VideoProcessor
    Logging -.-> ServoController

    %% --- Class Assignments ---
    class Webcam,VirtualCam,Arduino external;
    class EntryPoint entry;
    class MainWindow gui;
    class VideoProcessor,FaceTracker,GestureRecognizer vision;
    class ServoController hardware;
    class Config,Logging cross;
```

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python run.py
```

## Logs

Logs are written both to the console and to `logs/fazetrak.log` (rotated
automatically at 2 MB, keeping the last 3 files). Adjust the verbosity by
changing the `level` passed to `configure_logging()` in `run.py`.

## Notes on hardware requirements

- A webcam is required at the camera index configured in
  `config.CAMERA_INDEX` (default: `1`).
- A virtual camera output device is required (e.g. via `v4l2loopback` on
  Linux, or OBS Virtual Camera on Windows/macOS) for `pyvirtualcam` to work.
- The Arduino pan/tilt rig is optional — if it isn't connected, the app runs
  normally and simply reports "Not Connected" without crashing.

## Fixed issues (from the previous version)

1. **App would crash silently on launch with no visible error.** This was
   caused by `mediapipe`'s dependency on `opencv-contrib-python`, which
   bundles its own Qt platform plugins and hijacks
   `QT_QPA_PLATFORM_PLUGIN_PATH` on import, pointing PyQt5 at an incompatible
   plugin set. `run.py` now clears that environment variable before creating
   the `QApplication`.
2. **The app required a working camera and virtual camera device just to
   open the window.** The video processing thread is now created lazily,
   the first time "Start Tracking" is clicked, instead of eagerly in the
   window's constructor.
3. **`pyserial` was missing from `requirements.txt`** even though
   `servo_controller.py` depends on it (`import serial`). It's now listed
   explicitly.
