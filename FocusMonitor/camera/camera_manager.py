"""OpenCV camera wrapper that provides a safe webcam lifecycle."""

from __future__ import annotations

import os
from typing import Any

import cv2
import numpy as np

from FocusMonitor.utils.constants import CAMERA_HEIGHT, CAMERA_INDEX, CAMERA_WIDTH


class CameraManager:
    """Manage webcam access and frame acquisition using OpenCV."""

    def __init__(self, camera_index: int = CAMERA_INDEX, width: int = CAMERA_WIDTH, height: int = CAMERA_HEIGHT) -> None:
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self._capture: cv2.VideoCapture | None = None

    def open(self) -> bool:
        """Open the webcam and configure the capture resolution."""

        if self._capture is not None and self._capture.isOpened():
            return True

        backend = cv2.CAP_DSHOW if os.name == "nt" and hasattr(cv2, "CAP_DSHOW") else 0
        self._capture = cv2.VideoCapture(self.camera_index, backend)
        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        return self._capture.isOpened()

    def is_opened(self) -> bool:
        """Return whether the camera is currently open."""

        return self._capture is not None and self._capture.isOpened()

    def read_frame(self) -> tuple[bool, np.ndarray | None]:
        """Read one frame from the webcam and mirror it for a natural preview."""

        if not self.is_opened():
            return False, None

        assert self._capture is not None
        success, frame = self._capture.read()
        if not success or frame is None:
            return False, None
        return True, cv2.flip(frame, 1)

    def release(self) -> None:
        """Release the webcam safely."""

        if self._capture is not None:
            self._capture.release()
            self._capture = None

    def __enter__(self) -> "CameraManager":
        self.open()
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: Any) -> None:
        self.release()
