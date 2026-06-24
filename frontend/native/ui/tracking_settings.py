from __future__ import annotations

from pathlib import Path
from typing import Any, TYPE_CHECKING

import yaml
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from frontend.native.utils.config import (
    ABSENT_FRAMES,
    ACCENT,
    BLINK_MAX_FRAMES,
    BORDER,
    CAMERA_HEIGHT,
    CAMERA_INDEX,
    CAMERA_WIDTH,
    CARD,
    EAR_THRESHOLD,
    MAR_THRESHOLD,
    MUTED,
    NAVY,
    PITCH_DOWN,
    REQUIRED_FRAMES,
    SHOW_BBOX,
    SHOW_LANDMARKS,
    SHOW_OVERLAY,
    TEXT,
    YAW_LEFT,
    YAW_RIGHT,
)

if TYPE_CHECKING:
    from src.Features.VoxelStream_Module.services.ExpressionFSM import ExpressionFSM
    from src.Features.VoxelStream_Module.services.OCVCapture import OCVCapture


class TrackingSettingsDialog(QDialog):
    def __init__(
        self,
        parent: QWidget | None,
        fsm: ExpressionFSM,
        capture: OCVCapture,
    ) -> None:
        super().__init__(parent)
        self._fsm = fsm
        self._capture = capture
        self._camera_changed = False
        self.setWindowTitle("Tracking Settings")
        self.setMinimumWidth(360)
        self.setStyleSheet(
            f"QDialog {{ background-color: {CARD}; color: {TEXT}; }}"
        )
        self._build_ui()

    # ── UI ─────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(12)
        root.setContentsMargins(20, 20, 20, 20)

        title = QLabel("\u2699 Tracking Settings")
        title.setStyleSheet(
            f"font-size: 18px; font-weight: 800; color: white;"
        )
        root.addWidget(title)

        form = QFormLayout()
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignRight)

        def _spin(val: float, dec: int, lo: float, hi: float, step: float) -> QDoubleSpinBox:
            s = QDoubleSpinBox(self)
            s.setDecimals(dec)
            s.setRange(lo, hi)
            s.setSingleStep(step)
            s.setValue(val)
            s.setStyleSheet(
                f"background-color: {NAVY}; color: white; border: 1px solid {BORDER};"
                f" border-radius: 6px; padding: 4px 8px;"
            )
            return s

        # Camera
        self._cam_idx = QSpinBox(self)
        self._cam_idx.setRange(0, 10)
        self._cam_idx.setValue(CAMERA_INDEX)
        self._cam_idx.setStyleSheet(
            f"background-color: {NAVY}; color: white; border: 1px solid {BORDER};"
            f" border-radius: 6px; padding: 4px 8px;"
        )
        form.addRow("Camera Index:", self._cam_idx)

        self._ear = _spin(EAR_THRESHOLD, 2, 0.01, 1.0, 0.01)
        form.addRow("EAR Threshold:", self._ear)

        self._blink = QSpinBox(self)
        self._blink.setRange(5, 60)
        self._blink.setSingleStep(5)
        self._blink.setValue(BLINK_MAX_FRAMES)
        self._blink.setStyleSheet(self._cam_idx.styleSheet())
        form.addRow("Blink Max Frames:", self._blink)

        self._mar = _spin(MAR_THRESHOLD, 2, 0.01, 1.0, 0.01)
        form.addRow("MAR Threshold:", self._mar)

        self._yaw_l = _spin(YAW_LEFT, 1, -90.0, -1.0, 1.0)
        form.addRow("Yaw Left \u00b0:", self._yaw_l)

        self._yaw_r = _spin(YAW_RIGHT, 1, 1.0, 90.0, 1.0)
        form.addRow("Yaw Right \u00b0:", self._yaw_r)

        self._pitch_d = _spin(PITCH_DOWN, 1, -90.0, -1.0, 1.0)
        form.addRow("Pitch Down \u00b0:", self._pitch_d)

        self._absent = QSpinBox(self)
        self._absent.setRange(1, 500)
        self._absent.setValue(ABSENT_FRAMES)
        self._absent.setStyleSheet(self._cam_idx.styleSheet())
        form.addRow("Absent Frames:", self._absent)

        self._req = QSpinBox(self)
        self._req.setRange(1, 50)
        self._req.setValue(REQUIRED_FRAMES)
        self._req.setStyleSheet(self._cam_idx.styleSheet())
        form.addRow("Required Frames:", self._req)

        root.addLayout(form)

        # Display options
        sep = QLabel("Display")
        sep.setStyleSheet(
            f"font-size: 14px; font-weight: 700; color: white;"
            f" border-bottom: 1px solid {BORDER}; padding-bottom: 4px;"
        )
        root.addWidget(sep)

        def _checkbox(label: str, checked: bool) -> QCheckBox:
            cb = QCheckBox(label, self)
            cb.setChecked(checked)
            cb.setStyleSheet(
                f"color: {TEXT}; font-size: 13px; spacing: 8px;"
                f" QCheckBox::indicator {{ width: 18px; height: 18px; }}"
            )
            return cb

        self._cb_landmarks = _checkbox("Show Landmarks (dots)", SHOW_LANDMARKS)
        self._cb_bbox = _checkbox("Show Bounding Box", SHOW_BBOX)
        self._cb_overlay = _checkbox("Show Text Overlay", SHOW_OVERLAY)
        root.addWidget(self._cb_landmarks)
        root.addWidget(self._cb_bbox)
        root.addWidget(self._cb_overlay)

        root.addSpacing(8)

        # Buttons
        btns = QHBoxLayout()
        btns.setSpacing(10)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(
            f"background-color: {NAVY}; border: 1px solid {BORDER};"
            f" border-radius: 10px; padding: 10px 20px;"
            f" font-size: 13px; font-weight: 700; color: {MUTED};"
        )
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save")
        save_btn.setStyleSheet(
            f"background-color: {ACCENT}; border: none; border-radius: 10px;"
            f" padding: 10px 20px; font-size: 13px; font-weight: 700; color: white;"
        )
        save_btn.clicked.connect(self._on_save)

        btns.addWidget(cancel_btn)
        btns.addWidget(save_btn)
        root.addLayout(btns)

    # ── Actions ────────────────────────────────────────────

    def _on_save(self) -> None:
        self._fsm.EYE_CLOSE_THRESHOLD = self._ear.value()
        self._fsm.BLINK_MAX_FRAMES = self._blink.value()
        self._fsm.MOUTH_OPEN_THRESHOLD = self._mar.value()
        self._fsm.LOOKING_LEFT_THRESHOLD = self._yaw_l.value()
        self._fsm.LOOKING_RIGHT_THRESHOLD = self._yaw_r.value()
        self._fsm.LOOKING_DOWN_THRESHOLD = self._pitch_d.value()
        self._fsm.ABSENT_FRAMES = self._absent.value()
        self._fsm.REQUIRED_FRAMES = self._req.value()

        cam_idx = self._cam_idx.value()
        if cam_idx != CAMERA_INDEX and not self._capture.is_opened():
            self._capture.release()
            from src.Features.VoxelStream_Module.services.OCVCapture import OCVCapture

            self._capture = OCVCapture(cam_idx, CAMERA_WIDTH, CAMERA_HEIGHT)
            self._camera_changed = True

        self._persist()
        self.accept()

    @property
    def show_landmarks(self) -> bool:
        return self._cb_landmarks.isChecked()

    @property
    def show_bbox(self) -> bool:
        return self._cb_bbox.isChecked()

    @property
    def show_overlay(self) -> bool:
        return self._cb_overlay.isChecked()

    @property
    def updated_capture(self) -> Any:
        return self._capture

    def _persist(self) -> None:
        cfg_path = Path(__file__).resolve().parent.parent / "config.yaml"
        with open(cfg_path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        data.setdefault("tracking", {})
        data["tracking"]["ear_threshold"] = self._ear.value()
        data["tracking"]["blink_max_frames"] = self._blink.value()
        data["tracking"]["mar_threshold"] = self._mar.value()
        data["tracking"]["yaw_left"] = self._yaw_l.value()
        data["tracking"]["yaw_right"] = self._yaw_r.value()
        data["tracking"]["pitch_down"] = self._pitch_d.value()
        data["tracking"]["absent_frames"] = self._absent.value()
        data["tracking"]["required_frames"] = self._req.value()
        data["camera"]["index"] = self._cam_idx.value()
        data.setdefault("display", {})
        data["display"]["show_landmarks"] = self._cb_landmarks.isChecked()
        data["display"]["show_bbox"] = self._cb_bbox.isChecked()
        data["display"]["show_overlay"] = self._cb_overlay.isChecked()
        with open(cfg_path, "w", encoding="utf-8") as fh:
            yaml.safe_dump(data, fh, default_flow_style=False, allow_unicode=True)

    @property
    def camera_changed(self) -> bool:
        return self._camera_changed
