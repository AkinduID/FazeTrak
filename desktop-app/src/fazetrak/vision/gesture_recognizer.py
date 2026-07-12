"""
Simple hand-gesture classification used to toggle face tracking on and off.

Detects two gestures based on fingertip positions relative to the thumb:
  - an open palm (all fingertips above/higher than the thumb tip)   -> LOCK
  - a closed fist (all fingertips below/lower than the thumb tip)  -> UNLOCK

Note: MediaPipe's y-coordinates increase downward, so "higher on screen"
means a smaller y value.
"""

import logging
from enum import Enum
from typing import Optional

import mediapipe as mp

logger = logging.getLogger(__name__)

_HandLandmark = mp.solutions.hands.HandLandmark


class Gesture(str, Enum):
    """Gestures recognized by the tracker, used to lock/unlock face tracking."""

    LOCK = "lock"
    UNLOCK = "unlock"


def recognize_gesture(hand_landmarks) -> Optional[Gesture]:
    """
    Classify a single detected hand's landmarks as a LOCK or UNLOCK gesture.

    Args:
        hand_landmarks: A MediaPipe ``NormalizedLandmarkList`` for one hand,
            as returned in ``results.multi_hand_landmarks``.

    Returns:
        Gesture.LOCK if the hand shows an open palm, Gesture.UNLOCK if it
        shows a closed fist, or None if neither pattern is clearly matched
        (or no landmarks were provided).
    """
    if not hand_landmarks:
        return None

    thumb_tip_y = _fingertip_y(hand_landmarks, _HandLandmark.THUMB_TIP)
    index_tip_y = _fingertip_y(hand_landmarks, _HandLandmark.INDEX_FINGER_TIP)
    middle_tip_y = _fingertip_y(hand_landmarks, _HandLandmark.MIDDLE_FINGER_TIP)
    ring_tip_y = _fingertip_y(hand_landmarks, _HandLandmark.RING_FINGER_TIP)
    pinky_tip_y = _fingertip_y(hand_landmarks, _HandLandmark.PINKY_TIP)

    four_fingers_y = (index_tip_y, middle_tip_y, ring_tip_y, pinky_tip_y)

    is_open_palm = all(thumb_tip_y < finger_y for finger_y in four_fingers_y)
    is_closed_fist = all(finger_y < thumb_tip_y for finger_y in four_fingers_y)

    if is_open_palm:
        return Gesture.LOCK
    if is_closed_fist:
        return Gesture.UNLOCK
    return None


def _fingertip_y(hand_landmarks, landmark_id) -> float:
    """Extract the normalized y-coordinate of a single hand landmark."""
    return hand_landmarks.landmark[landmark_id].y
