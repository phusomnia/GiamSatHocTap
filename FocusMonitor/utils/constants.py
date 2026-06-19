"""Application constants for the FocusMonitor desktop app."""

from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "focus_monitor.db"
REPORTS_DIR = BASE_DIR / "reports"

APP_TITLE = "GiamSatHocTap - Focus Monitor"
WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 900
FRAME_INTERVAL_MS = 40
CAMERA_INDEX = 0
CAMERA_WIDTH = 960
CAMERA_HEIGHT = 540

FACE_DETECTION_CONFIDENCE = 0.6
FACE_MESH_CONFIDENCE = 0.5
FACE_LOST_SECONDS = 10.0
GAZE_AWAY_SECONDS = 5.0
DROWSY_SECONDS = 5.0
EAR_THRESHOLD = 0.21
ALERT_COOLDOWN_SECONDS = 5.0

NAVY = "#081a2f"
NAVY_DARK = "#040d1a"
NAVY_LIGHT = "#10345d"
ACCENT = "#45c2ff"
SUCCESS = "#2ecc71"
WARNING = "#f1c40f"
DANGER = "#ff6b6b"
TEXT = "#ecf4ff"
MUTED = "#9ab2cc"
CARD = "#0f2743"
BORDER = "#1b3f67"
