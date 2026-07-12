#!/usr/bin/env python3
"""
FazeTrak entry point.

Usage:
    python run.py
"""

import logging
import os
import sys
from pathlib import Path

# Allow running directly from a source checkout without installing the
# package first (`pip install -e .`), by putting `src/` on the import path.
_SRC_DIRECTORY = Path(__file__).resolve().parent / "src"
if str(_SRC_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(_SRC_DIRECTORY))

# --- Bugfix -------------------------------------------------------------
# `mediapipe` depends on `opencv-contrib-python`, which bundles its own Qt
# platform plugins and points QT_QPA_PLATFORM_PLUGIN_PATH at them as a side
# effect of `import cv2`. Those plugins are not guaranteed to be compatible
# with the PyQt5 build actually in use, and when they aren't, QApplication
# aborts the process immediately (a native SIGABRT, not a Python exception)
# with no window ever appearing. Clearing the variable before creating the
# QApplication lets PyQt5 fall back to its own bundled, matching plugins.
#
# This must happen after `cv2` has been imported (directly or transitively)
# but before `QApplication` is constructed, so it's done here in the entry
# point rather than buried in application code.
import cv2  # noqa: E402  (import order is required for the fix above)

os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH", None)
# -------------------------------------------------------------------------

from PyQt5.QtWidgets import QApplication  # noqa: E402

from fazetrak.gui.main_window import MainWindow  # noqa: E402
from fazetrak.logging_config import configure_logging  # noqa: E402


def main() -> int:
    """Configure logging, launch the Qt application, and run the main window."""
    configure_logging(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("Starting FazeTrak.")
    application = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    return application.exec_()


if __name__ == "__main__":
    sys.exit(main())
