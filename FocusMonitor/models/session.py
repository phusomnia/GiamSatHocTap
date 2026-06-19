"""Core data models and enums for focus tracking sessions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import numpy as np


class FocusStatus(str, Enum):
    """High-level state of the current attention estimate."""

    FOCUSING = "FOCUSING"
    LOST_FOCUS = "LOST_FOCUS"
    DROWSY = "DROWSY"


class GazeDirection(str, Enum):
    """Estimated gaze direction from the webcam frame."""

    LOOKING_CENTER = "LOOKING_CENTER"
    LOOKING_LEFT = "LOOKING_LEFT"
    LOOKING_RIGHT = "LOOKING_RIGHT"
    LOOKING_DOWN = "LOOKING_DOWN"
    UNKNOWN = "UNKNOWN"


@dataclass(slots=True)
class FaceDetectionResult:
    """Face detection result returned by the face detector."""

    detected: bool
    face_count: int
    bounding_boxes: list[tuple[int, int, int, int]]
    fps: float


@dataclass(slots=True)
class EyeDetectionResult:
    """Eye detection result returned by the eye detector."""

    ear: float
    eyes_closed: bool
    closed_seconds: float
    drowsy: bool


@dataclass(slots=True)
class GazeDetectionResult:
    """Gaze detection result returned by the gaze detector."""

    direction: GazeDirection
    focus: bool
    away_seconds: float


@dataclass(slots=True)
class FocusStateSnapshot:
    """Combined frame-level focus state used by the focus service."""

    frame: np.ndarray
    status: FocusStatus
    message: str
    face_detected: bool
    gaze_direction: GazeDirection
    drowsy: bool
    focus_active: bool
    alert_required: bool = False


@dataclass(slots=True)
class FocusMetrics:
    """Aggregated session metrics kept in memory and shown in the UI."""

    focus_time: float = 0.0
    lost_time: float = 0.0
    drowsy_time: float = 0.0
    total_time: float = 0.0

    @property
    def focus_score(self) -> float:
        """Return the percentage of focused time over the total session time."""

        if self.total_time <= 0:
            return 0.0
        return (self.focus_time / self.total_time) * 100.0


@dataclass(slots=True)
class SessionRecord:
    """Persisted study session stored in SQLite."""

    start_time: datetime
    end_time: datetime
    focus_time: float
    lost_time: float
    focus_score: float
    id: int | None = None
