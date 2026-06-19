"""Eye detector that estimates eye closure and identifies drowsiness."""

from __future__ import annotations

import time

import cv2
import numpy as np

from FocusMonitor.models.session import EyeDetectionResult
from FocusMonitor.utils.constants import DROWSY_SECONDS, EAR_THRESHOLD


class EyeDetector:
    """Track eye closure state using OpenCV eye cascades."""

    def __init__(self, ear_threshold: float = EAR_THRESHOLD, drowsy_seconds: float = DROWSY_SECONDS) -> None:
        eye_cascade_path = cv2.data.haarcascades + "haarcascade_eye_tree_eyeglasses.xml"
        self._eye_detector = cv2.CascadeClassifier(eye_cascade_path)
        self._ear_threshold = ear_threshold
        self._drowsy_seconds = drowsy_seconds
        self._closed_since: float | None = None

    def detect(self, frame: np.ndarray) -> EyeDetectionResult:
        """Return the EAR, eye closure duration, and drowsiness state."""

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detected_eyes = self._eye_detector.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=6, minSize=(20, 20))

        eye_count = len(detected_eyes)
        if eye_count == 0:
            self._closed_since = None
            return EyeDetectionResult(ear=0.0, eyes_closed=False, closed_seconds=0.0, drowsy=False)

        eye_area = sum(width * height for _, _, width, height in detected_eyes)
        face_area = float(frame.shape[0] * frame.shape[1])
        ear = min(1.0, eye_area / max(face_area * 0.08, 1.0))
        eyes_closed = eye_count < 2 or ear < self._ear_threshold

        now = time.monotonic()
        if eyes_closed:
            if self._closed_since is None:
                self._closed_since = now
            closed_seconds = now - self._closed_since
        else:
            self._closed_since = None
            closed_seconds = 0.0

        return EyeDetectionResult(
            ear=ear,
            eyes_closed=eyes_closed,
            closed_seconds=closed_seconds,
            drowsy=closed_seconds >= self._drowsy_seconds,
        )

    def annotate(self, frame: np.ndarray, result: EyeDetectionResult) -> np.ndarray:
        """Overlay EAR and drowsiness state on the frame."""

        annotated = frame.copy()
        status_text = "DROWSY" if result.drowsy else ("EYES CLOSED" if result.eyes_closed else "EYES OPEN")
        status_color = (0, 0, 255) if result.drowsy else ((0, 255, 255) if result.eyes_closed else (180, 255, 180))

        cv2.putText(
            annotated,
            f"EAR: {result.ear:.3f}",
            (20, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            annotated,
            status_text,
            (20, 135),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            status_color,
            2,
            cv2.LINE_AA,
        )
        return annotated
