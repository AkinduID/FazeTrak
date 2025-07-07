import mediapipe as mp

def detect_hand_gesture(hand_landmarks):
    """Detects if the hand is showing an open palm (lock) or fist (unlock)."""
    if hand_landmarks:
        thumb_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP].y
        index_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP].y
        middle_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP].y
        ring_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_TIP].y
        pinky_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_TIP].y

        if thumb_tip < index_tip and thumb_tip < middle_tip and thumb_tip < ring_tip and thumb_tip < pinky_tip:
            return "lock"
        elif index_tip < thumb_tip and middle_tip < thumb_tip and ring_tip < thumb_tip and pinky_tip < thumb_tip:
            return "unlock"
    return None 