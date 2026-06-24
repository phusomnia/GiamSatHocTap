from __future__ import annotations

import time
from typing import Any

import cv2
import numpy as np
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.Features.VoxelStream_Module.services.OCVCapture import OCVCapture
from src.Features.VoxelStream_Module.services.Detector import Detector
from src.Features.VoxelStream_Module.services.Extractor import Extractor
from src.Features.VoxelStream_Module.services.ExpressionFSM import ExpressionFSM
from src.Features.VoxelStream_Module.services.Renderer import Renderer
from src.Features.VoxelStream_Module.services.FaceState import FaceState
from src.Features.VoxelStream_Module.services.HeadPoseEstimator import HeadPoseEstimator
from src.SharedKernel.persistence.SessionManager import SessionManager
from src.SharedKernel.persistence.StudySessionRepo import StudySessionRepo

from src.Features.VoxelStream_Module.services.FocusAnalyzer import FocusLevel
from src.Features.VoxelStream_Module.services.FaceAuth import FaceAuthenticator

from frontend.native.ui.history_window import HistoryPage
from frontend.native.ui.tracking_settings import TrackingSettingsDialog
from frontend.native.utils.config import (
    ABSENT_FRAMES,
    ACCENT,
    APP_TITLE,
    BORDER,
    CAMERA_HEIGHT,
    CAMERA_INDEX,
    CAMERA_WIDTH,
    CARD,
    DANGER,
    EAR_THRESHOLD,
    FRAME_INTERVAL_MS,
    MAR_THRESHOLD,
    MUTED,
    NAVY,
    NAVY_DARK,
    NAVY_LIGHT,
    PITCH_DOWN,
    REQUIRED_FRAMES,
    SHOW_BBOX,
    SHOW_LANDMARKS,
    SHOW_OVERLAY,
    SUCCESS,
    TEXT,
    WARNING,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    YAW_LEFT,
    YAW_RIGHT,
)

SIDEBAR_WIDTH = 200
NAV_ICONS = {"monitor": "\U0001F4F7", "history": "\U0001F4CA"}


class Dashboard(QMainWindow):
    def __init__(self, db: StudySessionRepo, session_manager: SessionManager) -> None:
        super().__init__()
        self.capture = OCVCapture(CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT)
        self.extractor = Extractor()
        self.fsm = ExpressionFSM()
        self.fsm.EYE_CLOSE_THRESHOLD = EAR_THRESHOLD
        self.fsm.MOUTH_OPEN_THRESHOLD = MAR_THRESHOLD
        self.fsm.LOOKING_LEFT_THRESHOLD = YAW_LEFT
        self.fsm.LOOKING_RIGHT_THRESHOLD = YAW_RIGHT
        self.fsm.LOOKING_DOWN_THRESHOLD = PITCH_DOWN
        self.fsm.ABSENT_FRAMES = ABSENT_FRAMES
        self.fsm.REQUIRED_FRAMES = REQUIRED_FRAMES
        self.show_landmarks = SHOW_LANDMARKS
        self.show_bbox = SHOW_BBOX
        self.show_overlay = SHOW_OVERLAY
        self.renderer = Renderer()
        self.head_pose_estimator = HeadPoseEstimator()
        self.db = db
        self.session_manager = session_manager

        self.detector = Detector()
        self.detector_ctx = self.detector.__enter__()

        self._is_running = False
        self._last_tick = time.perf_counter()
        self._timer = QTimer(self)
        self._timer.setInterval(FRAME_INTERVAL_MS)
        self._timer.timeout.connect(self._process_frame)

        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self._build_ui()

        self.face_auth = FaceAuthenticator()
        self.is_registered = False
        self.auth_warning = False
        self.auth_frame_count = 0

    # ── UI ──────────────────────────────────────────────

    def _build_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._build_sidebar(root)
        self._build_content(root)

        self.setStyleSheet(
            f"""
            QMainWindow, QWidget {{ background-color: {NAVY}; color: {TEXT}; }}
            QLabel#metricCard {{
                background-color: {CARD};
                border-radius: 16px;
                border: 1px solid {BORDER};
                padding: 12px;
            }}
            QPushButton#navBtn {{
                border: none;
                border-radius: 12px;
                padding: 14px 18px;
                font-size: 14px;
                font-weight: 600;
                color: {MUTED};
                text-align: left;
                background-color: transparent;
            }}
            QPushButton#navBtn:hover {{
                background-color: {NAVY_LIGHT};
                color: white;
            }}
            QPushButton#navBtn:checked {{
                background-color: {NAVY_LIGHT};
                color: white;
            }}
            """
        )

    def _build_sidebar(self, root: QHBoxLayout) -> None:
        sidebar = QWidget(self)
        sidebar.setFixedWidth(SIDEBAR_WIDTH)
        sidebar.setStyleSheet(f"background-color: {NAVY_DARK};")

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(6)

        logo = QLabel("GSHT", self)
        logo.setStyleSheet(
            f"font-size: 22px; font-weight: 900; color: {ACCENT}; padding: 8px 4px 20px 4px;"
        )
        layout.addWidget(logo)

        self.nav_monitor = self._nav_button("\U0001F4F7  Monitor")
        self.nav_history = self._nav_button("\U0001F4CA  History")
        self.nav_monitor.clicked.connect(lambda: self._switch_page(0))
        self.nav_history.clicked.connect(lambda: self._switch_page(1))
        self.nav_monitor.setChecked(True)

        layout.addWidget(self.nav_monitor)
        layout.addWidget(self.nav_history)
        layout.addStretch()
        root.addWidget(sidebar)

    def _nav_button(self, text: str) -> QPushButton:
        btn = QPushButton(text, self)
        btn.setObjectName("navBtn")
        btn.setCheckable(True)
        return btn

    def _build_content(self, root: QHBoxLayout) -> None:
        self.stack = QStackedWidget(self)
        self.stack.addWidget(self._build_monitor_page())
        self.stack.addWidget(HistoryPage(self.db))
        root.addWidget(self.stack, 1)

    def _switch_page(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        self.nav_monitor.setChecked(index == 0)
        self.nav_history.setChecked(index == 1)

    # ── Monitor page ─────────────────────────────────────

    def _build_monitor_page(self) -> QWidget:
        page = QWidget(self)
        root = QVBoxLayout(page)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(16)

        title = QLabel("GiamSatHocTap", self)
        title.setStyleSheet("font-size: 30px; font-weight: 800; color: white;")
        subtitle = QLabel("Live attention tracking via MediaPipe", self)
        subtitle.setStyleSheet(f"font-size: 14px; color: {MUTED};")
        root.addWidget(title)
        root.addWidget(subtitle)

        body = QHBoxLayout()
        body.setSpacing(16)

        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(CAMERA_WIDTH, CAMERA_HEIGHT)
        self.video_label.setStyleSheet(
            f"background-color: {CARD}; border-radius: 18px; border: 1px solid {BORDER}; color: {MUTED};"
        )
        self.video_label.setText("Starting camera\u2026")

        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)

        self.score_card = self._card("Focus Percentage", "\u2014")
        self.focus_card = self._card("Focus State", "\u2014")
        self.time_card = self._card("Session Time", "0s")
        self.state_card = self._card("Face State", "\u2014")
        self.pitch_card = self._card("Pitch", "\u2014")
        self.yaw_card = self._card("Yaw", "\u2014")
        self.roll_card = self._card("Roll", "\u2014")
        self.ear_card = self._card("EAR", "\u2014")
        self.mar_card = self._card("MAR", "\u2014")
        self.distraction_card = self._card("Distractions", "0")
        self.fps_card = self._card("FPS", "\u2014")

        for w in (
            self.score_card, self.focus_card, self.time_card, self.state_card,
            self.pitch_card, self.yaw_card, self.roll_card,
            self.ear_card, self.mar_card, self.distraction_card,
            self.fps_card,
        ):
            right_panel.addWidget(w)

        controls = QHBoxLayout()
        controls.setSpacing(10)
        self.start_btn = self._button("Start", SUCCESS)
        self.stop_btn = self._button("Stop", DANGER)
        self.start_btn.clicked.connect(self._start_session)
        self.stop_btn.clicked.connect(self._stop_session)
        self.stop_btn.setEnabled(False)
        controls.addWidget(self.start_btn)
        controls.addWidget(self.stop_btn)
        self.settings_btn = QPushButton("\u2699", self)
        self.settings_btn.setFixedWidth(44)
        self.settings_btn.setToolTip("Tracking Settings")
        self.settings_btn.setStyleSheet(
            f"background-color: {CARD}; border: 1px solid {BORDER};"
            f" border-radius: 12px; font-size: 18px; color: {MUTED};"
        )
        self.settings_btn.clicked.connect(self._open_settings_dialog)
        controls.addWidget(self.settings_btn)
        right_panel.addLayout(controls)

        right_panel.addStretch(1)
        body.addWidget(self.video_label, 2)
        body.addLayout(right_panel, 1)
        root.addLayout(body)
        return page

    def _card(self, title: str, value: str) -> QLabel:
        w = QLabel(self)
        w.setObjectName("metricCard")
        w.setMinimumHeight(68)
        w.setWordWrap(True)
        w.setText(self._card_html(title, value))
        return w

    def _card_html(self, title: str, value: str) -> str:
        return (
            f"<div style='font-size:13px; color:{MUTED};'>{title}</div>"
            f"<div style='font-size:22px; font-weight:800; margin-top:4px;'>{value}</div>"
        )

    def _button(self, text: str, color: str) -> QPushButton:
        btn = QPushButton(text, self)
        btn.setStyleSheet(
            f"background-color: {color}; border: none; border-radius: 12px;"
            f" padding: 12px 16px; font-size: 14px; font-weight: 700; color: white;"
        )
        return btn

    # ── Settings dialog ──────────────────────────────────

    def _open_settings_dialog(self) -> None:
        dialog = TrackingSettingsDialog(self, self.fsm, self.capture)
        if dialog.exec_() == QDialog.Accepted:
            if dialog.camera_changed:
                self.capture = dialog.updated_capture
            self.show_landmarks = dialog.show_landmarks
            self.show_bbox = dialog.show_bbox
            self.show_overlay = dialog.show_overlay

    # ── Session lifecycle ────────────────────────────────

    def _start_session(self) -> None:
        if self._is_running:
            return
        if not self.capture.is_opened():
            QMessageBox.critical(self, "Camera Error", "Cannot open webcam.")
            return
        self.session_manager.start()
        self._is_running = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self._timer.start()

    def _stop_session(self) -> None:
        if not self._is_running:
            return
        self._timer.stop()
        self._is_running = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        session = self.session_manager.stop()
        if session:
            QMessageBox.information(
                self,
                "Session Saved",
                f"Focus Percentage: {session.focus_score:.1f}%\n"
                f"Duration: {session.duration}s\n"
                f"Distractions: {session.distraction_count}",
            )
        self._clear_cards()

        #RESET TRẠNG THÁI KHUÔN MẶT KHI DỪNG PHIÊN
        self.is_registered = False       
        self.auth_fail_count = 0         
        self.auth_warning = False        
        
        # Xóa sạch dữ liệu khuôn mặt cũ trong FaceAuthenticator
        if hasattr(self, 'face_auth'):
            self.face_auth.registered_embedding = None
            
        if hasattr(self, 'register_attempt_count'):
            self.register_attempt_count = 0   

    def _clear_cards(self) -> None:
        for card, title in (
            (self.score_card, "Focus Percentage"), (self.focus_card, "Focus State"),
            (self.time_card, "Session Time"), (self.state_card, "Face State"),
            (self.pitch_card, "Pitch"), (self.yaw_card, "Yaw"),
            (self.roll_card, "Roll"), (self.ear_card, "EAR"),
            (self.mar_card, "MAR"), (self.distraction_card, "Distractions"),
            (self.fps_card, "FPS"),
        ):
            card.setText(self._card_html(title, "\u2014"))

    # ── Frame processing ─────────────────────────────────

    def _process_frame(self) -> None:
        if not self._is_running:
            return

        frame = self.capture.read()
        if frame is None:
            return

        now = time.perf_counter()
        fps = 1.0 / max(now - self._last_tick, 0.001)
        self._last_tick = now

        #Chạy bộ detector gốc của đồ án trước để biết chắc chắn có mặt hay không
        result = self.detector_ctx.detect(frame, self.capture.timestamp())

        state = FaceState.NORMAL
        metrics = None

        # TRƯỜNG HỢP 1: CAMERA NHÌN THẤY CÓ KHUÔN MẶT
        if result.face_landmarks:
            
            # A. Nếu CHƯA ĐĂNG KÝ -> Tiến hành tự động đăng ký
            if not getattr(self, 'is_registered', False):
                cv2.putText(frame, "PHAT HIEN MAT - DANG TRICH XUAT...", (20, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                
                if not hasattr(self, 'register_attempt_count'):
                    self.register_attempt_count = 0
                self.register_attempt_count += 1

                if self.register_attempt_count % 15 == 0:
                    success = self.face_auth.register_face(frame)
                    if success:
                        self.is_registered = True
                        print("✅ Tự động đăng ký khuôn mặt thành công!")
                
                self._render_frame(frame)
                return

            # B. Nếu ĐÃ ĐĂNG KÝ -> Tiến hành kiểm tra danh tính định kỳ (3 giây/lần)
            self.auth_frame_count = getattr(self, 'auth_frame_count', 0) + 1
            if self.auth_frame_count % 90 == 0:
                is_correct_user = self.face_auth.verify_face(frame)
                if not is_correct_user:
                    self.auth_warning = True
                    self.auth_fail_count = getattr(self, 'auth_fail_count', 0) + 1
                    print(f"⚠️ Phát hiện sai người lần {self.auth_fail_count}!")
                else:
                    self.auth_warning = False
                    self.auth_fail_count = 0

            # Nếu vi phạm liên tiếp 3 lần (9 giây toàn người lạ) -> KHÓA 
            if getattr(self, 'auth_fail_count', 0) >= 3:
                self.handle_auth_violation()
                return

            # Hiển thị cảnh báo nếu đang có người lạ ngồi trước máy
            if getattr(self, 'auth_warning', False):
                cv2.putText(frame, f"WARNING: UNAUTHORIZED ({self.auth_fail_count}/3)", (20, 170), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            # PHÂN TÍCH TẬP TRUNG 
            for idx, landmarks in enumerate(result.face_landmarks):
                metrics = self.extractor.extract(landmarks)
                if (
                    result.facial_transformation_matrixes
                    and idx < len(result.facial_transformation_matrixes)
                ):
                    tf_matrix = result.facial_transformation_matrixes[idx]
                    pitch, yaw, roll = self.head_pose_estimator.estimate(tf_matrix)
                    metrics.pitch = pitch
                    metrics.yaw = yaw
                    metrics.roll = roll
                state = self.fsm.update(metrics)
                frame = self.renderer.render(
                    frame, landmarks, state, metrics,
                    show_landmarks=self.show_landmarks,
                    show_bbox=self.show_bbox,
                    show_overlay=self.show_overlay,
                )
                
        # TRƯỜNG HỢP 2: KHÔNG TÌM THẤY KHUÔN MẶT NÀO TRÊN CAMERA
        else:
            # Nếu chưa đăng ký mà camera trống trơn -> Bắt buộc người dùng đưa mặt vào
            if not getattr(self, 'is_registered', False):
                cv2.putText(frame, "KHONG TIM THAY KHUON MAT", (20, 150), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                cv2.putText(frame, "Vui long dua mat vao camera de bat dau...", (20, 190), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                self._render_frame(frame)
                return

            # Nếu đã đăng ký nhưng rời khỏi  -> Cũng tính cảnh cáo
            self.auth_frame_count = getattr(self, 'auth_frame_count', 0) + 1
            if self.auth_frame_count % 90 == 0:
                self.auth_warning = True
                self.auth_fail_count = getattr(self, 'auth_fail_count', 0) + 1
                print(f"⚠️ Không tìm thấy người học lần {self.auth_fail_count}!")

            if getattr(self, 'auth_fail_count', 0) >= 3:
                self.handle_auth_violation()
                return

            if getattr(self, 'auth_warning', False):
                cv2.putText(frame, f"WARNING: NO FACE DETECTED ({self.auth_fail_count}/3)", (20, 150), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            # --- LOGIC GỐC KHI KHÔNG CÓ MẶT ---
            state = self.fsm.update(None)
            frame = self.renderer.render_no_face(
                frame, state,
                show_overlay=self.show_overlay,
            )

        self.session_manager.update(state)
        self._render_frame(frame)
        self._update_cards(state, metrics, fps)

    def _update_cards(self, state: FaceState, metrics, fps: float) -> None:
        stats = self.session_manager.get_current_stats()

        self.score_card.setText(
            self._card_html("Focus Percentage", f"{stats.get('focus_score', 100):.1f}%")
        )

        focus_level = stats.get("focus_level", "FOCUSING")
        focus_color = SUCCESS
        if focus_level == FocusLevel.DROWSY.value:
            focus_color = DANGER
        elif focus_level == FocusLevel.LOST_FOCUS.value:
            focus_color = MUTED
        self.focus_card.setText(self._card_html("Focus State", focus_level))
        self.focus_card.setStyleSheet(
            f"background-color: {CARD}; border-radius: 16px; border: 1px solid {BORDER};"
            f" padding: 12px; color: {focus_color};"
        )

        self.time_card.setText(
            self._card_html("Session Time", f"{stats.get('elapsed_seconds', 0)}s")
        )

        state_color = SUCCESS
        if state == FaceState.EYES_CLOSED:
            state_color = WARNING
        elif state == FaceState.YAWNING:
            state_color = DANGER
        elif state in (FaceState.LOOKING_DOWN, FaceState.ABSENT):
            state_color = MUTED

        self.state_card.setText(self._card_html("Face State", state.value))
        self.state_card.setStyleSheet(
            f"background-color: {CARD}; border-radius: 16px; border: 1px solid {BORDER};"
            f" padding: 12px; color: {state_color};"
        )

        if metrics and metrics.pitch is not None:
            self.pitch_card.setText(self._card_html("Pitch", f"{metrics.pitch:.1f}\u00b0"))
            self.yaw_card.setText(self._card_html("Yaw", f"{metrics.yaw:.1f}\u00b0"))
            self.roll_card.setText(self._card_html("Roll", f"{metrics.roll:.1f}\u00b0"))
        else:
            self.pitch_card.setText(self._card_html("Pitch", "\u2014"))
            self.yaw_card.setText(self._card_html("Yaw", "\u2014"))
            self.roll_card.setText(self._card_html("Roll", "\u2014"))

        self.ear_card.setText(
            self._card_html("EAR", f"{metrics.ear:.3f}" if metrics else "\u2014")
        )
        self.mar_card.setText(
            self._card_html("MAR", f"{metrics.mar:.3f}" if metrics else "\u2014")
        )
        self.distraction_card.setText(
            self._card_html("Distractions", str(stats.get("distraction_count", 0)))
        )
        self.fps_card.setText(self._card_html("FPS", f"{fps:.1f}"))

    def _render_frame(self, frame: np.ndarray) -> None:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(img).scaled(
            self.video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.video_label.setPixmap(pix)   

    def handle_auth_violation(self):
        """Hàm xử lý khi phát hiện sai người / vắng mặt quá lâu"""
        
        # 1. Dừng camera
        self._is_running = False 
        
        # 2. Bật Popup cảnh báo 
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("CẢNH BÁO")
        msg.setText("Phát hiện người lạ hoặc bạn đã rời khỏi vị trí quá lâu!")
        msg.setInformativeText("Hệ thống đã bị khóa. Vui lòng nhấn OK và nhìn thẳng vào camera để xác thực lại danh tính!")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        
        # 3. ÉP BUỘC PHẢI QUÉT LẠI KHUÔN MẶT 
        self.is_registered = False  
        self.auth_fail_count = 0    
        self.auth_warning = False   
        self._is_running = True          
    # ── Lifecycle ────────────────────────────────────────

    def closeEvent(self, event: Any) -> None:
        self._timer.stop()
        if self._is_running:
            self.session_manager.stop()
        self.detector.__exit__(None, None, None)
        self.capture.release()
        event.accept()
