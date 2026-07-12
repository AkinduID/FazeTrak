"""
Pure geometry/logic for converting a detected face position into a servo
correction. Deliberately has no knowledge of OpenCV, MediaPipe, threads, or
serial ports, so it can be unit tested in isolation.
"""

import logging
from dataclasses import dataclass

from fazetrak import config

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ServoAngles:
    """A pan/tilt angle pair, in degrees."""

    pan_degrees: int
    tilt_degrees: int


class FaceTracker:
    """
    Computes the servo angles needed to (re)center a detected face in frame.

    The tracker is initialized with the frame's dimensions so it knows where
    "centered" means, and produces incremental corrections each time a new
    face position is reported, similar to a simple proportional controller.
    """

    def __init__(self, frame_width: int, frame_height: int) -> None:
        self.frame_center_x = frame_width // 2
        self.frame_center_y = frame_height // 2

    def compute_correction(
        self,
        face_center_x: float,
        face_center_y: float,
        current_angles: ServoAngles,
    ) -> ServoAngles:
        """
        Given the current detected face position and the servos' current
        angles, compute the new angles that nudge the face back toward the
        center of frame.

        Faces within ``config.TRACKING_TOLERANCE_PIXELS`` of center are
        treated as already centered (no correction, to avoid jitter).
        """
        horizontal_offset = abs(face_center_x - self.frame_center_x)
        vertical_offset = abs(face_center_y - self.frame_center_y)

        horizontal_step = self._proportional_step(horizontal_offset, self.frame_center_x)
        vertical_step = self._proportional_step(vertical_offset, self.frame_center_y)

        new_pan = current_angles.pan_degrees
        new_tilt = current_angles.tilt_degrees

        if face_center_x < self.frame_center_x - config.TRACKING_TOLERANCE_PIXELS:
            new_pan -= horizontal_step
        elif face_center_x > self.frame_center_x + config.TRACKING_TOLERANCE_PIXELS:
            new_pan += horizontal_step

        if face_center_y < self.frame_center_y - config.TRACKING_TOLERANCE_PIXELS:
            new_tilt -= vertical_step
        elif face_center_y > self.frame_center_y + config.TRACKING_TOLERANCE_PIXELS:
            new_tilt += vertical_step

        new_pan = self._clamp_angle(new_pan)
        new_tilt = self._clamp_angle(new_tilt)

        if (new_pan, new_tilt) != (current_angles.pan_degrees, current_angles.tilt_degrees):
            logger.debug(
                "Face correction: pan %d->%d, tilt %d->%d",
                current_angles.pan_degrees,
                new_pan,
                current_angles.tilt_degrees,
                new_tilt,
            )

        return ServoAngles(pan_degrees=new_pan, tilt_degrees=new_tilt)

    @staticmethod
    def _proportional_step(offset_pixels: float, axis_center: float) -> int:
        """Scale the maximum step size by how far off-center the face is."""
        if axis_center == 0:
            return config.TRACKING_STEP_DEGREES
        proportion = offset_pixels / axis_center
        return max(1, int(proportion * config.TRACKING_STEP_DEGREES))

    @staticmethod
    def _clamp_angle(angle_degrees: int) -> int:
        """Keep a servo angle within its physically valid range."""
        return max(
            config.MIN_SERVO_ANGLE_DEGREES,
            min(config.MAX_SERVO_ANGLE_DEGREES, angle_degrees),
        )
