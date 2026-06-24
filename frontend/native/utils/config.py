from pathlib import Path

from src.Infrastructure.Config import Config

_cfg = Config().load_env_yaml(
    str(Path(__file__).resolve().parent.parent / "config.yaml")
)

BASE_DIR = Path(__file__).resolve().parent.parent

APP_TITLE = _cfg.app.title
WINDOW_WIDTH = _cfg.app.window_width
WINDOW_HEIGHT = _cfg.app.window_height
CAMERA_INDEX = _cfg.camera.index
CAMERA_WIDTH = _cfg.camera.width
CAMERA_HEIGHT = _cfg.camera.height
FRAME_INTERVAL_MS = _cfg.camera.frame_interval_ms
FACE_LOST_SECONDS = _cfg.session.face_lost_seconds
ALERT_COOLDOWN_SECONDS = _cfg.session.alert_cooldown_seconds
DB_PATH = str(BASE_DIR / _cfg.session.db_path)

EAR_THRESHOLD = _cfg.tracking.ear_threshold
MAR_THRESHOLD = _cfg.tracking.mar_threshold
BLINK_MAX_FRAMES = _cfg.tracking.blink_max_frames
YAW_LEFT = _cfg.tracking.yaw_left
YAW_RIGHT = _cfg.tracking.yaw_right
PITCH_DOWN = _cfg.tracking.pitch_down
ABSENT_FRAMES = _cfg.tracking.absent_frames
REQUIRED_FRAMES = _cfg.tracking.required_frames

SHOW_LANDMARKS = _cfg.display.show_landmarks
SHOW_BBOX = _cfg.display.show_bbox
SHOW_OVERLAY = _cfg.display.show_overlay

NAVY = _cfg.colors.navy
NAVY_LIGHT = _cfg.colors.navy_light
NAVY_DARK = _cfg.colors.navy_dark
ACCENT = _cfg.colors.accent
SUCCESS = _cfg.colors.success
WARNING = _cfg.colors.warning
DANGER = _cfg.colors.danger
TEXT = _cfg.colors.text
MUTED = _cfg.colors.muted
CARD = _cfg.colors.card
BORDER = _cfg.colors.border
