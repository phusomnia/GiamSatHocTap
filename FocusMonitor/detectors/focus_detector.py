"""Combined focus-state logic built on face, eye and gaze results."""

from __future__ import annotations

import time

import cv2
import numpy as np

from FocusMonitor.models.session import EyeDetectionResult, FaceDetectionResult, FocusStateSnapshot, GazeDetectionResult
from FocusMonitor.models.session import FocusStatus
from FocusMonitor.utils.constants import DROWSY_SECONDS, FACE_LOST_SECONDS


class FocusDetector:
    """Decide the current focus state from detector outputs and timers."""

    def __init__(self) -> None:
        self._face_missing_since: float | None = None
        self._drowsy_since: float | None = None

    def evaluate(
        self,
        frame: np.ndarray,
        face_result: FaceDetectionResult,
        eye_result: EyeDetectionResult,
        gaze_result: GazeDetectionResult,
    ) -> FocusStateSnapshot:
        """Evaluate the overall focus state and annotate it on the frame."""

        current_time = time.monotonic()
        message = ""
        alert_required = False

        if face_result.detected:
            self._face_missing_since = None
        elif self._face_missing_since is None:
            self._face_missing_since = current_time

        face_missing_duration = 0.0 if self._face_missing_since is None else current_time - self._face_missing_since

        if eye_result.drowsy:
            if self._drowsy_since is None:
                self._drowsy_since = current_time
            drowsy_duration = current_time - self._drowsy_since
        else:
            self._drowsy_since = None
            drowsy_duration = 0.0

        if not face_result.detected:
            status = FocusStatus.LOST_FOCUS
            message = "NO FACE"
        elif eye_result.drowsy:
            status = FocusStatus.DROWSY
            message = "DROWSY"
            alert_required = drowsy_duration >= DROWSY_SECONDS
        elif gaze_result.focus:
            status = FocusStatus.FOCUSING
            message = "FOCUSING"
        else:
            status = FocusStatus.LOST_FOCUS
            message = f"LOOKING {gaze_result.direction.value.replace('LOOKING_', '')}"

        if face_missing_duration >= FACE_LOST_SECONDS:
            alert_required = True
        if drowsy_duration >= DROWSY_SECONDS:
            alert_required = True

        annotated = frame.copy()
        cv2.putText(
            annotated,
            f"STATUS: {status.value}",
            (20, 205),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (80, 200, 120) if status == FocusStatus.FOCUSING else (255, 107, 107),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            annotated,
            f"DETAIL: {message}",
            (20, 240),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        return FocusStateSnapshot(
            frame=annotated,
            status=status,
            message=message,
            face_detected=face_result.detected,
            gaze_direction=gaze_result.direction,
            drowsy=eye_result.drowsy,
            focus_active=status == FocusStatus.FOCUSING,
            alert_required=alert_required,
        )
