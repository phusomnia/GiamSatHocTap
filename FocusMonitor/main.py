"""Application entry point for FocusMonitor."""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from PyQt5.QtWidgets import QApplication

from FocusMonitor.camera.camera_manager import CameraManager
from FocusMonitor.database.sqlite_manager import SQLiteManager
from FocusMonitor.detectors.eye_detector import EyeDetector
from FocusMonitor.detectors.face_detector import FaceDetector
from FocusMonitor.detectors.focus_detector import FocusDetector
from FocusMonitor.detectors.gaze_detector import GazeDetector
from FocusMonitor.services.focus_service import FocusService
from FocusMonitor.services.statistics_service import StatisticsService
from FocusMonitor.ui.dashboard import Dashboard
from FocusMonitor.utils.constants import DATABASE_PATH, REPORTS_DIR


def main() -> int:
    """Create the Qt application and show the dashboard window."""

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    database = SQLiteManager(str(DATABASE_PATH))
    application = QApplication(sys.argv)
    dashboard = Dashboard(
        camera_manager=CameraManager(),
        face_detector=FaceDetector(),
        eye_detector=EyeDetector(),
        gaze_detector=GazeDetector(),
        focus_detector=FocusDetector(),
        focus_service=FocusService(),
        database=database,
        statistics_service=StatisticsService(),
    )
    dashboard.show()
    return application.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
