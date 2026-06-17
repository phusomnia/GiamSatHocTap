"""Gaze detector that classifies the user's attention direction."""

from __future__ import annotations

import time

import cv2
import numpy as np

from FocusMonitor.models.session import GazeDetectionResult, GazeDirection
from FocusMonitor.utils.constants import GAZE_AWAY_SECONDS


class GazeDetector:
    """Classify gaze direction and track how long the user stays off-center."""

    def __init__(self, away_seconds: float = GAZE_AWAY_SECONDS) -> None:
        eye_cascade_path = cv2.data.haarcascades + "haarcascade_eye_tree_eyeglasses.xml"
        self._eye_detector = cv2.CascadeClassifier(eye_cascade_path)
        self._away_seconds_threshold = away_seconds
        self._off_center_since: float | None = None

    def detect(self, frame: np.ndarray) -> GazeDetectionResult:
        """Return the gaze direction and how long it has stayed away from center."""

        direction = self._classify_direction(frame)
        is_center = direction == GazeDirection.LOOKING_CENTER

        now = time.monotonic()
        if is_center:
            self._off_center_since = None
            away_seconds = 0.0
        else:
            if self._off_center_since is None:
                self._off_center_since = now
            away_seconds = now - self._off_center_since

        return GazeDetectionResult(direction=direction, focus=is_center, away_seconds=away_seconds)

    def annotate(self, frame: np.ndarray, result: GazeDetectionResult) -> np.ndarray:
        """Overlay the gaze direction on the frame."""

        annotated = frame.copy()
        cv2.putText(
            annotated,
            f"GAZE: {result.direction.value}",
            (20, 170),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        return annotated

    def _classify_direction(self, frame: np.ndarray) -> GazeDirection:
        """Infer gaze direction from the relative position of detected eyes."""

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detected_eyes = self._eye_detector.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=6, minSize=(20, 20))

        if len(detected_eyes) == 0:
            return GazeDirection.UNKNOWN

        frame_width = frame.shape[1]
        frame_height = frame.shape[0]
        eye_centers = [((x + width / 2.0), (y + height / 2.0)) for x, y, width, height in detected_eyes]
        average_x = sum(point[0] for point in eye_centers) / len(eye_centers)
        average_y = sum(point[1] for point in eye_centers) / len(eye_centers)

        horizontal_ratio = average_x / max(frame_width, 1)
        vertical_ratio = average_y / max(frame_height, 1)

        if vertical_ratio > 0.62:
            return GazeDirection.LOOKING_DOWN
        if horizontal_ratio < 0.32:
            return GazeDirection.LOOKING_LEFT
        if horizontal_ratio > 0.68:
            return GazeDirection.LOOKING_RIGHT
        return GazeDirection.LOOKING_CENTER
