"""Main PyQt5 dashboard for webcam-based focus monitoring."""

from __future__ import annotations

import sys
import time
from datetime import datetime
from typing import Any

import cv2
import numpy as np
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from FocusMonitor.camera.camera_manager import CameraManager
from FocusMonitor.database.sqlite_manager import SQLiteManager
from FocusMonitor.detectors.eye_detector import EyeDetector
from FocusMonitor.detectors.face_detector import FaceDetector
from FocusMonitor.detectors.focus_detector import FocusDetector
from FocusMonitor.detectors.gaze_detector import GazeDetector
from FocusMonitor.models.session import FocusStatus, FocusStateSnapshot
from FocusMonitor.services.focus_service import FocusService
from FocusMonitor.services.statistics_service import StatisticsService
from FocusMonitor.ui.history_window import HistoryWindow
from FocusMonitor.utils.constants import (
    ACCENT,
    ALERT_COOLDOWN_SECONDS,
    APP_TITLE,
    BORDER,
    CARD,
    CAMERA_HEIGHT,
    CAMERA_WIDTH,
    DANGER,
    DROWSY_SECONDS,
    FACE_LOST_SECONDS,
    FRAME_INTERVAL_MS,
    MUTED,
    NAVY,
    NAVY_LIGHT,
    SUCCESS,
    TEXT,
    WARNING,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)


class Dashboard(QMainWindow):
    """Display the webcam feed, metrics and session controls."""

    def __init__(
        self,
        camera_manager: CameraManager,
        face_detector: FaceDetector,
        eye_detector: EyeDetector,
        gaze_detector: GazeDetector,
        focus_detector: FocusDetector,
        focus_service: FocusService,
        database: SQLiteManager,
        statistics_service: StatisticsService,
    ) -> None:
        super().__init__()
        self._camera_manager = camera_manager
        self._face_detector = face_detector
        self._eye_detector = eye_detector
        self._gaze_detector = gaze_detector
        self._focus_detector = focus_detector
        self._focus_service = focus_service
        self._database = database
        self._statistics_service = statistics_service
        self._history_window: HistoryWindow | None = None
        self._timer = QTimer(self)
        self._timer.setInterval(FRAME_INTERVAL_MS)
        self._timer.timeout.connect(self._process_frame)
        self._last_tick = time.monotonic()
        self._last_alert = 0.0
        self._is_running = False

        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self._build_ui()

    def _build_ui(self) -> None:
        """Build the dashboard widgets and layout."""

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(18, 18, 18, 18)
        root_layout.setSpacing(16)

        title_label = QLabel("GiamSatHocTap FocusMonitor", self)
        title_label.setStyleSheet("font-size: 30px; font-weight: 800; color: white;")
        subtitle_label = QLabel("Real-time webcam attention tracking", self)
        subtitle_label.setStyleSheet(f"font-size: 14px; color: {MUTED};")

        root_layout.addWidget(title_label)
        root_layout.addWidget(subtitle_label)

        body_layout = QHBoxLayout()
        body_layout.setSpacing(16)

        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(CAMERA_WIDTH, CAMERA_HEIGHT)
        self.video_label.setStyleSheet(
            f"background-color: {CARD}; border-radius: 18px; border: 1px solid {BORDER}; color: {MUTED};"
        )
        self.video_label.setText("Webcam preview will appear here")

        metrics_container = QVBoxLayout()
        metrics_container.setSpacing(12)
        self.score_label = self._create_metric_card("Focus Score", "0.0%")
        self.focus_time_label = self._create_metric_card("Focus Time", "0.0 s")
        self.lost_time_label = self._create_metric_card("Lost Time", "0.0 s")
        self.status_label = self._create_metric_card("Status", "IDLE")

        metrics_container.addWidget(self.score_label)
        metrics_container.addWidget(self.focus_time_label)
        metrics_container.addWidget(self.lost_time_label)
        metrics_container.addWidget(self.status_label)

        controls_widget = QWidget(self)
        controls_layout = QHBoxLayout(controls_widget)
        controls_layout.setSpacing(12)
        self.start_button = self._create_button("Start", SUCCESS)
        self.stop_button = self._create_button("Stop", DANGER)
        self.history_button = self._create_button("View History", ACCENT)
        self.start_button.clicked.connect(self.start_monitoring)
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.history_button.clicked.connect(self.open_history)
        controls_layout.addWidget(self.start_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addWidget(self.history_button)

        metrics_container.addWidget(controls_widget)
        metrics_container.addStretch(1)

        body_layout.addWidget(self.video_label, 2)
        body_layout.addLayout(metrics_container, 1)
        root_layout.addLayout(body_layout)

        self.setStyleSheet(
            f"""
            QMainWindow {{ background-color: {NAVY}; }}
            QWidget {{ color: {TEXT}; }}
            QLabel#metricCard {{
                background-color: {CARD};
                border-radius: 16px;
                border: 1px solid {BORDER};
                padding: 14px;
            }}
            QPushButton {{
                border: none;
                border-radius: 14px;
                padding: 14px 18px;
                font-size: 15px;
                font-weight: 700;
                color: white;
            }}
            QPushButton:hover {{ background-color: {NAVY_LIGHT}; }}
            """
        )

    def _create_metric_card(self, title: str, value: str) -> QLabel:
        """Create a card-like label used to show KPI values."""

        widget = QLabel(self)
        widget.setObjectName("metricCard")
        widget.setMinimumHeight(102)
        widget.setWordWrap(True)
        widget.setText(
            f"<div style='font-size:14px; color:{MUTED};'>{title}</div>"
            f"<div style='font-size:28px; font-weight:800; margin-top:8px;'>{value}</div>"
        )
        return widget

    def _create_button(self, text: str, color: str) -> QPushButton:
        """Create a themed action button."""

        button = QPushButton(text, self)
        button.setStyleSheet(f"background-color: {color};")
        return button

    def start_monitoring(self) -> None:
        """Start the webcam pipeline and reset the active session."""

        if self._is_running:
            return

        if not self._camera_manager.open():
            QMessageBox.critical(self, "Camera Error", "Unable to open the webcam.")
            return

        self._focus_service.start(datetime.now())
        self._last_tick = time.monotonic()
        self._is_running = True
        self._timer.start()

    def stop_monitoring(self) -> None:
        """Stop monitoring and persist the current session."""

        if not self._is_running:
            return

        self._timer.stop()
        self._camera_manager.release()
        self._is_running = False

        try:
            session = self._focus_service.stop(datetime.now())
        except RuntimeError:
            return

        self._database.save_session(session)
        self._show_session_summary(session.focus_time, session.lost_time, session.focus_score)
        self._update_status_card("STOPPED")
        self._render_placeholder()

    def open_history(self) -> None:
        """Open the history statistics window."""

        self._history_window = HistoryWindow(self._database, self._statistics_service)
        self._history_window.show()

    def _process_frame(self) -> None:
        """Read a frame, run detectors, update scores and refresh the UI."""

        success, frame = self._camera_manager.read_frame()
        if not success or frame is None:
            self._update_status_card("NO CAMERA")
            self._render_placeholder()
            return

        current_monotonic = time.monotonic()
        current_datetime = datetime.now()

        face_result = self._face_detector.detect(frame)
        rendered = self._face_detector.annotate(frame, face_result)

        eye_result = self._eye_detector.detect(frame)
        rendered = self._eye_detector.annotate(rendered, eye_result)

        gaze_result = self._gaze_detector.detect(frame)
        rendered = self._gaze_detector.annotate(rendered, gaze_result)

        focus_state = self._focus_detector.evaluate(rendered, face_result, eye_result, gaze_result)

        self._focus_service.update(focus_state, current_datetime)
        self._refresh_metrics(focus_state)
        self._render_frame(focus_state.frame)
        self._handle_alerts(focus_state, current_monotonic)

    def _refresh_metrics(self, focus_state: FocusStateSnapshot) -> None:
        """Refresh KPI cards from the latest session values."""

        metrics = self._focus_service.metrics
        self.score_label.setText(
            f"<div style='font-size:14px; color:{MUTED};'>Focus Score</div>"
            f"<div style='font-size:28px; font-weight:800; margin-top:8px;'>{metrics.focus_score:.1f}%</div>"
        )
        self.focus_time_label.setText(
            f"<div style='font-size:14px; color:{MUTED};'>Focus Time</div>"
            f"<div style='font-size:28px; font-weight:800; margin-top:8px;'>{metrics.focus_time:.1f}s</div>"
        )
        self.lost_time_label.setText(
            f"<div style='font-size:14px; color:{MUTED};'>Lost Time</div>"
            f"<div style='font-size:28px; font-weight:800; margin-top:8px;'>{metrics.lost_time:.1f}s</div>"
        )
        self._update_status_card(focus_state.status.value)

    def _render_frame(self, frame: np.ndarray) -> None:
        """Convert an OpenCV frame into a Qt pixmap."""

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = rgb_frame.shape
        bytes_per_line = channel * width
        image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image).scaled(
            self.video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.video_label.setPixmap(pixmap)

    def _render_placeholder(self) -> None:
        """Show a neutral placeholder when the camera is not producing frames."""

        placeholder = np.zeros((CAMERA_HEIGHT, CAMERA_WIDTH, 3), dtype=np.uint8)
        placeholder[:, :] = (15, 39, 67)
        cv2.putText(
            placeholder,
            "Waiting for camera",
            (50, CAMERA_HEIGHT // 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        self._render_frame(placeholder)

    def _handle_alerts(self, focus_state: FocusStateSnapshot, current_monotonic: float) -> None:
        """Trigger the warning sound and popup when attention is too low."""

        if not focus_state.alert_required:
            return

        if current_monotonic - self._last_alert < ALERT_COOLDOWN_SECONDS:
            return

        self._last_alert = current_monotonic
        QApplication.beep()
        QMessageBox.warning(self, "Focus Alert", "Please focus on your work")

    def _update_status_card(self, value: str) -> None:
        """Update the status card text with a new value."""

        self.status_label.setText(
            f"<div style='font-size:14px; color:{MUTED};'>Status</div>"
            f"<div style='font-size:28px; font-weight:800; margin-top:8px;'>{value}</div>"
        )

    def _show_session_summary(self, focus_time: float, lost_time: float, focus_score: float) -> None:
        """Display a short summary after the session is saved."""

        QMessageBox.information(
            self,
            "Session Saved",
            f"Focus Score: {focus_score:.1f}%\nFocus Time: {focus_time:.1f}s\nLost Time: {lost_time:.1f}s",
        )

    def closeEvent(self, event: Any) -> None:  # type: ignore[override]
        """Make sure the camera is released before closing the window."""

        self.stop_monitoring()
        self._camera_manager.release()
        event.accept()
