"""Face detector with bounding boxes and FPS rendering."""

from __future__ import annotations

import time

import cv2
import numpy as np

from FocusMonitor.models.session import FaceDetectionResult


class FaceDetector:
    """Detect faces with OpenCV Haar cascades and annotate the frame."""

    def __init__(self) -> None:
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self._detector = cv2.CascadeClassifier(cascade_path)
        self._last_tick = time.perf_counter()
        self._fps = 0.0

    def detect(self, frame: np.ndarray) -> FaceDetectionResult:
        """Detect faces in the frame and compute the current FPS."""

        height, width = frame.shape[:2]
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detections = self._detector.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

        now = time.perf_counter()
        delta = now - self._last_tick
        self._last_tick = now
        if delta > 0:
            self._fps = 1.0 / delta

        boxes: list[tuple[int, int, int, int]] = []
        for x, y, box_width, box_height in detections:
            boxes.append((int(x), int(y), int(box_width), int(box_height)))

        return FaceDetectionResult(
            detected=bool(boxes),
            face_count=len(boxes),
            bounding_boxes=boxes,
            fps=self._fps,
        )

    def annotate(self, frame: np.ndarray, result: FaceDetectionResult) -> np.ndarray:
        """Draw face bounding boxes and FPS on the frame."""

        annotated = frame.copy()
        for x, y, box_width, box_height in result.bounding_boxes:
            cv2.rectangle(annotated, (x, y), (x + box_width, y + box_height), (80, 200, 120), 2)
            cv2.putText(
                annotated,
                "Face",
                (x, max(20, y - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (80, 200, 120),
                2,
                cv2.LINE_AA,
            )

        cv2.putText(
            annotated,
            f"FPS: {result.fps:.1f}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            annotated,
            f"Faces: {result.face_count}",
            (20, 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        return annotated
