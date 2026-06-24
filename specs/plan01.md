# Native Frontend Module

Desktop application sử dụng PyQt5 + MediaPipe Face Landmarker để theo dõi tập trung thời gian thực qua webcam.

---

# 1. Kiến trúc

```
OCVCapture                     (src/Features/VoxelStream_Module/services/OCVCapture.py)
    ↓
Detector                       (src/Features/VoxelStream_Module/services/Detector.py)
    ↓
Extractor                      (src/Features/VoxelStream_Module/services/Extractor.py)
    ↓
ExpressionFSM                  (src/Features/VoxelStream_Module/services/ExpressionFSM.py)
    ↓
Renderer / FocusAnalyzer      (render frame + tính điểm tập trung)
    ↓
SessionService                (quản lý phiên học, focus score)
    ↓
SQLite + PyQt5 Dashboard      (lưu dữ liệu + hiển thị)
```

Tất cả service từ VoxelStream được **import trực tiếp** — không qua API.

---

# 2. Cấu trúc thư mục

```
frontend/native/
├── lain.py                       # Entry point, DI wiring
```

---

# 3. Các thành phần

## 3.1. main.py

Entry point. Import trực tiếp từ VoxelStream module:

```python
from src.Features.VoxelStream_Module.services.OCVCapture import OCVCapture
from src.Features.VoxelStream_Module.services.Detector import Detector
from src.Features.VoxelStream_Module.services.Extractor import Extractor
from src.Features.VoxelStream_Module.services.ExpressionFSM import ExpressionFSM
from src.Features.VoxelStream_Module.services.Renderer import Renderer
```

Khởi tạo PyQt5 `QApplication`, wiring dependencies, show `Dashboard`.

### Luồng khởi động

```python
app = QApplication(sys.argv)
dashboard = Dashboard(
    capture=OCVCapture(),
    extractor=Extractor(),
    fsm=ExpressionFSM(),
    renderer=Renderer(),
    session_service=SessionService(),
    database=SQLiteManager(DB_PATH),
    statistics_service=StatisticsService(),
)
dashboard.show()
sys.exit(app.exec_())
```

---

## 3.2. Dashboard (`ui/dashboard.py`)

Kế thừa `QMainWindow` (tương tự `FocusMonitor/ui/dashboard.py`).

### Layout

```
┌──────────────────────────────────────────────────┐
│  GiamSatHocTap - Native Monitor                 │
│  Real-time webcam attention tracking            │
├────────────────────────┬─────────────────────────┤
│                        │  Focus Score   78.3%    │
│    [WEBCAM FEED]       │  Focus Time   120.5s   │
│                        │  Lost Time     34.2s   │
│                        │  State       FOCUSING  │
│                        │                        │
│                        │  [Start] [Stop] [Hist] │
└────────────────────────┴─────────────────────────┘
```

### Vòng lặp xử lý (QTimer @33ms = ~30fps)

```python
def _process_frame(self):
    frame = self.capture.read()                   # OCVCapture
    if frame is None:
        return

    # MediaPipe detection
    with Detector() as detector:
        result = detector.detect(frame, self.capture.timestamp())

    state = FaceState.NORMAL
    metrics = None

    if result.face_landmarks:
        for landmarks in result.face_landmarks:
            metrics = self.extractor.extract(landmarks)
            state = self.fsm.update(metrics)
            frame = self.renderer.render(frame, landmarks, state, metrics)

    # Focus analysis
    focus_state = self._analyze_focus(frame, result.face_landmarks, state)
    self.session_service.update(focus_state, datetime.now())

    # Update UI
    self._render_frame(frame)
    self._refresh_metrics()
```

### FocusAnalyzer (tích hợp trong Dashboard)

Kết hợp kết quả từ các service để xác định trạng thái tập trung:

| Điều kiện | Trạng thái |
|---|---|
| Có face + state = NORMAL | FOCUSING |
| state = EYES_CLOSED | DROWSY |
| state = YAWNING | DROWSY |
| Không face > 3 giây | LOST_FOCUS |

---

## 3.3. SessionService (`services/session_service.py`)

Tương tự `FocusMonitor/services/focus_service.py`.

### Chức năng

- `start()` — reset counters, ghi start_time
- `update(focus_state, timestamp)` — accumulate focus/lost/drowsy time
- `stop()` — trả về `SessionRecord`, reset counters

### Công thức

```python
focus_score = (focus_time / total_time) * 100
```

### SessionRecord

```python
@dataclass
class SessionRecord:
    start_time: datetime
    end_time: datetime
    focus_time: float
    lost_time: float
    drowsy_time: float
    focus_score: float
```

---

## 3.4. SQLiteManager (`database/sqlite_manager.py`)

Tương tự `FocusMonitor/database/sqlite_manager.py`.

### Bảng

```sql
CREATE TABLE study_sessions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time  TEXT NOT NULL,
    end_time    TEXT NOT NULL,
    focus_time  REAL NOT NULL,
    lost_time   REAL NOT NULL,
    drowsy_time REAL NOT NULL DEFAULT 0,
    focus_score REAL NOT NULL
);
```

### CRUD

- `save_session(record: SessionRecord)`
- `get_all_sessions() -> list[SessionRecord]`
- `get_sessions_by_date_range(start, end)`

---

## 3.5. HistoryWindow (`ui/history_window.py`)

Hiển thị biểu đồ matplotlib:

- **Daily focus score** — cột focus_score theo ngày
- **Weekly study time** — tổng thời gian học theo tuần
- **Behavior breakdown** — pie chart (focus, lost, drowsy)

---

## 3.6. Constants (`utils/constants.py`)

```python
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_INDEX = 0
FRAME_INTERVAL_MS = 33          # ~30fps

# VoxelStream thresholds (giữ nguyên từ ExpressionFSM)
EYE_CLOSE_THRESHOLD = 0.20
MOUTH_OPEN_THRESHOLD = 0.03
REQUIRED_FRAMES = 4

# Session
FACE_LOST_SECONDS = 3.0
ALERT_COOLDOWN_SECONDS = 5.0

# UI colors (tone navy, giống FocusMonitor)
NAVY = "#081a2f"
ACCENT = "#45c2ff"
SUCCESS = "#2ecc71"
DANGER = "#ff6b6b"
TEXT = "#ecf4ff"
MUTED = "#9ab2cc"
CARD = "#0f2743"
BORDER = "#1b3f67"

# Paths
DB_PATH = Path(__file__).resolve().parent.parent / "database" / "focus_monitor.db"
```

---

# 4. Dependencies

```text
opencv-python
mediapipe
numpy
PyQt5
matplotlib
```

Giống `FocusMonitor/requirements.txt` — không cần thêm thư viện mới.

---

# 5. So sánh với FocusMonitor hiện tại

| Thành phần | FocusMonitor (Haar Cascade) | Native (VoxelStream) |
|---|---|---|
| Face detection | Haar cascade bounding box | MediaPipe 478 landmarks |
| Eye detection | Haar cascade + heuristic EAR | Chính xác từ landmark indices |
| Gaze | Heuristic bounding box ratio | Chưa có (sẽ thêm HeadPoseEstimator) |
| Drowsiness | EAR threshold + closed_seconds | ExpressionFSM + hysteresis |
| UI framework | PyQt5 | PyQt5 (giống) |
| Database | SQLite | SQLite (giống) |
| Focus score | focus/lost time ratio | focus/lost time ratio (giống) |

**Lợi thế của bản Native:**
- Accuracy cao hơn nhờ 478 landmark
- FSM hysteresis giảm nhấp nháy
- Dễ mở rộng (head pose, gaze, blendshapes)
- Tái sử dụng trực tiếp service từ VoxelStream

---

# 6. Kế hoạch triển khai

## Bước 1: Tạo khung project
- `main.py` với PyQt5 QApplication + Dashboard skeleton
- `utils/constants.py`
- `requirements.txt`

## Bước 2: Dashboard + vòng lặp video
- Kế thừa `QMainWindow`
- `QTimer` @33ms gọi `OCVCapture.read()` → hiển thị lên `QLabel`
- Kiểm tra kết nối camera

## Bước 3: Tích hợp VoxelStream pipeline
- Import `Detector`, `Extractor`, `ExpressionFSM`, `Renderer`
- Chạy pipeline trong `_process_frame()`
- Hiển thị frame đã render (landmarks + state + metrics)

## Bước 4: FocusAnalyzer + SessionService
- Xác định trạng thái tập trung từ face state
- `SessionService` tích lũy thời gian focus/lost/drowsy
- Update metric cards trên Dashboard

## Bước 5: Database + History
- `SQLiteManager` CRUD
- `HistoryWindow` với matplotlib charts

## Bước 6: Start/Stop controls + alerts
- Start → mở camera, bắt đầu session
- Stop → đóng camera, lưu session
- Alert popup nếu mất tập trung quá lâu

---

# 7. Nguyên tắc

- **Không gọi API** — import trực tiếp service class từ `src/Features/VoxelStream_Module/`
- **Giữ đúng convention** — đặt tên file, class, style code giống FocusMonitor
- **Không thêm dependency mới** — chỉ dùng những thư viện đã có
