# Module VoxelStream

Pipeline phân tích mức độ tập trung qua khuôn mặt thời gian thực sử dụng webcam và MediaPipe Face Landmarker.

## Pipeline

```
Capture → Detect → Extract → HeadPoseEstimator → FSM → FocusAnalyzer → Render → Display
                                      ↓
                                SessionManager
                                      ↓
                              StudySessionRepo
                                      ↓
                                  SQLite
```

## Thuật toán

### Vòng lặp xử lý từng khung hình

Thuật toán chính (`VoxelStreamProc.run_tracker`) chạy ở tốc độ FPS của webcam:

```
for each frame:
  1. CAPTURE    – Đọc khung hình BGR từ webcam (1280×720, đã lật)
  2. DETECT     – Chuyển BGR→RGB, chạy MediaPipe FaceLandmarker (chế độ VIDEO)
  3. EXTRACT    – Tính EAR (Eye Aspect Ratio) & MAR (Mouth Aspect Ratio)
                  từ lưới landmark 478 điểm
  4. HEAD POSE  – Phân rã ma trận biến đổi khuôn mặt 4×4 thành
                  pitch/yaw/roll (góc Euler ZYX, độ)
   5. FSM        – Đưa các chỉ số vào máy trạng thái hysteresis → FaceState
  6. ANALYZE    – Đưa FaceState vào FocusAnalyzer → phần trăm tập trung
   7. RENDER     – Chú thích khung hình với chữ/chấm landmark (tắt mặc định)
  8. DISPLAY    – Hiển thị khung hình qua cv2.imshow("Focus Analysis")
```

### Logic quyết định trạng thái (ExpressionFSM)

FSM áp dụng debouncing hysteresis: **4 khung hình liên tiếp** phải đồng nhất trước khi chuyển trạng thái.

**Thứ tự ưu tiên** khi đánh giá metrics (head pose được ưu tiên):

```
yaw vượt ±25°?              → bỏ qua kiểm tra ngáp/nhắm mắt (chỉ xét hướng nhìn)
MAR > 0.5?                   → YAWNING (ngáp)
EAR < 0.20?                  → EYES_CLOSED (nhắm mắt)
pitch < -20°?                → LOOKING_DOWN (nhìn xuống)
yaw < -25°?                  → LOOKING_LEFT (nhìn trái)
yaw > 25°?                   → LOOKING_RIGHT (nhìn phải)
còn lại                      → NORMAL (bình thường)
```

**Không phát hiện khuôn mặt:** bộ đếm vắng mặt tăng lên mỗi khung hình. Sau **90 khung hình (~3s)** trạng thái chuyển thành `ABSENT` (cũng qua hysteresis 4 khung hình).

Xem chi tiết công thức tại [Hysteresis State Transition](#hysteresis-state-transition) và [Absent Timeout](#absent-timeout).

## Công thức tính toán

### Khoảng cách Euclidean (2D)

Khoảng cách giữa 2 điểm landmark trên mặt phẳng ảnh:

$$d(p_1, p_2) = \sqrt{(x_1 - x_2)^2 + (y_1 - y_2)^2}$$

Công thức này được dùng trong mọi phép tính EAR, MAR, và các khoảng cách landmark khác.

### EAR (Eye Aspect Ratio)

Tỉ lệ khung mắt, đo độ mở của mắt:

$$EAR = \frac{\|p_2 - p_6\| + \|p_3 - p_5\|}{2 \cdot \|p_1 - p_4\|}$$

với các landmark MediaPipe:

| Mắt | p₁ | p₂ | p₃ | p₄ | p₅ | p₆ |
|---|---|---|---|---|---|---|
| Trái | 33 | 160 | 158 | 133 | 153 | 144 |
| Phải | 362 | 385 | 387 | 263 | 373 | 380 |

EAR trung bình:

$$ear = \frac{left\_ear + right\_ear}{2}$$

Giá trị EAR càng thấp (≈ 0) khi nhắm mắt, càng cao (≈ 0.25–0.35) khi mở mắt.
Ngưỡng phát hiện nhắm mắt: `EAR < 0.20`.

### MAR (Mouth Aspect Ratio)

Tỉ lệ khung miệng, đo độ mở của miệng:

$$MAR = \frac{d(13, 14)}{d(78, 308)} = \frac{\sqrt{(x_{13} - x_{14})^2 + (y_{13} - y_{14})^2}}{\sqrt{(x_{78} - x_{308})^2 + (y_{78} - y_{308})^2}}$$

Trong đó:
- `13` – môi trên, `14` – môi dưới (khoảng cách dọc)
- `78` – khóe miệng trái, `308` – khóe miệng phải (khoảng cách ngang)

Giá trị MAR tăng khi ngáp hoặc nói. Ngưỡng phát hiện ngáp: `MAR > 0.5`.

### Head Pose – Góc Euler từ ma trận xoay

Ma trận xoay $R_{3 \times 3}$ được trích từ ma trận biến đổi khuôn mặt $4 \times 4$ của MediaPipe:

$$R = \begin{bmatrix} R_{00} & R_{01} & R_{02} \\ R_{10} & R_{11} & R_{12} \\ R_{20} & R_{21} & R_{22} \end{bmatrix}$$

Tính góc xoay theo quy ước ZYX:

$$sy = \sqrt{R_{00}^2 + R_{10}^2}$$

**Trường hợp thường** ($sy \geq 10^{-6}$):

$$
\begin{aligned}
pitch &= \text{atan2}(R_{21}, R_{22}) \times \frac{180}{\pi} \\
yaw   &= \text{atan2}(-R_{20}, sy) \times \frac{180}{\pi} \\
roll  &= \text{atan2}(R_{10}, R_{00}) \times \frac{180}{\pi}
\end{aligned}
$$

**Trường hợp gimbal lock** ($sy < 10^{-6}$):

$$
\begin{aligned}
pitch &= \text{atan2}(-R_{12}, R_{11}) \times \frac{180}{\pi} \\
yaw   &= \text{atan2}(-R_{20}, sy) \times \frac{180}{\pi} \\
roll  &= 0
\end{aligned}
$$

| Góc | Ý nghĩa | Dương | Âm |
|---|---|---|---|
| Pitch | Gật đầu (lên/xuống) | Ngửa lên | Cúi xuống |
| Yaw | Lắc đầu (trái/phải) | Quay phải | Quay trái |
| Roll | Nghiêng đầu | Nghiêng phải | Nghiêng trái |

### Hysteresis State Transition

FSM chống rung lắc (debounce) với yêu cầu **4 khung hình liên tiếp** đồng nhất:

$$
\text{state}_{t} =
\begin{cases}
\text{state}_{t-1} & \text{nếu } target = \text{state}_{t-1} \\
target & \text{nếu } counter \geq REQUIRED\_FRAMES \\
\text{state}_{t-1} & \text{nếu } counter < REQUIRED\_FRAMES
\end{cases}
$$

Logic chuyển trạng thái:

```
if target == current_state:
    counter = 0
else:
    counter += 1
    if counter >= 4:
        current_state = target
        counter = 0
return current_state
```

### Absent Timeout

Khi không phát hiện khuôn mặt, bộ đếm tăng dần:

$$\text{state} = \begin{cases} ABSENT & \text{nếu } absent\_counter \geq 90 \\ \text{state}_{t-1} & \text{ngược lại} \end{cases}$$

90 khung hình ≈ 3 giây ở 30 FPS.

### Focus Score

Điểm tập trung dựa trên tỉ lệ khung hình tập trung:

$$\text{focus\_score} = \frac{\text{focusing\_frames}}{\text{total\_frames}} \times 100$$

với:

$$\text{focusing\_frames} = \sum \mathbf{1}[state \in \{NORMAL, LOOKING\_LEFT, LOOKING\_RIGHT\}]$$

### Focus Level

Phân loại mức tập trung theo trạng thái hiện tại:

$$
\text{focus\_level} =
\begin{cases}
FOCUSING  & \text{nếu } state \in \{NORMAL, LOOKING\_LEFT, LOOKING\_RIGHT\} \\
DROWSY    & \text{nếu } state \in \{EYES\_CLOSED, YAWNING\} \\
LOST\_FOCUS & \text{nếu } state \in \{LOOKING\_DOWN, ABSENT\}
\end{cases}
$$

### Đếm sự kiện mất tập trung

Mỗi lần chuyển trạng thái sang trạng thái tiêu cực, các bộ đếm tăng tương ứng:

| Chuyển sang | `distraction_count` | Bộ đếm riêng |
|---|---|---|
| `EYES_CLOSED` | +1 | `eye_close_count++` |
| `YAWNING` | – | `yawn_count++` |
| `LOOKING_LEFT` | – | `looking_left_count++` |
| `LOOKING_RIGHT` | – | `looking_right_count++` |
| `LOOKING_DOWN` | +1 | `looking_down_count++` |
| `ABSENT` | +1 | `absent_count++` |

### Luồng lưu trữ

```
SessionManager.start() → ghi lại start_time
  ↓
SessionManager.update(state) → cung cấp FocusAnalyzer cho mỗi khung hình
  ↓
SessionManager.stop() → ghi StudySession vào SQLite qua StudySessionRepo
  ↓
5 REST endpoints truy vấn dữ liệu đã lưu
```

## Cấu trúc thư mục

```
VoxelStream_Module/
├── config/
│   └── face_landmarker.task        # Mô hình landmark khuôn mặt MediaPipe tiền huấn luyện
├── controllers/
│   └── VoxelStreamController.py    # FastAPI controller (5 endpoints)
├── dto/
│   └── VoxelStreamDTO.py           # Model phản hồi API Pydantic
├── handlers/
│   └── VoxelStreamProc.py          # Điều phối xử lý chính (vòng lặp pipeline)
├── models/
│   └── StudySession.py             # Dataclass dữ liệu phiên học
├── services/
│   ├── interfaces/
│   │   └── FrameSource.py          # Nguồn khung hình trừu tượng (ABC)
│   ├── OCVCapture.py               # Chụp webcam OpenCV (1280×720, đã lật)
│   ├── Detector.py                 # Context manager MediaPipe FaceLandmarker
│   ├── Extractor.py                # Tính EAR/MAR từ 478 landmark
│   ├── HeadPoseEstimator.py        # Pitch/Yaw/Roll từ ma trận biến đổi 4×4
│   ├── Metrics.py                  # Class dữ liệu FaceMetrics (ear, mar, pitch/yaw/roll)
│   ├── FaceState.py                # Enum FaceState (7 trạng thái)
│   ├── ExpressionFSM.py            # Máy trạng thái dựa trên hysteresis
│   ├── FocusAnalyzer.py            # Phần trăm tập trung & bộ đếm sự kiện hành vi
│   ├── Renderer.py                 # Chú thích khung hình (landmarks, bbox, text)
│   └── SessionManager.py (đã chuyển) # → src/SharedKernel/persistence/SessionManager.py
├── __init__.py
└── VoxelStream_Module.md
```

> **Ghi chú:** `SessionManager` và `StudySessionRepo` nằm ở `src/SharedKernel/persistence/` — được dùng chung giữa các module.

## Components

### VoxelStreamController (`controllers/VoxelStreamController.py`)

FastAPI controller được đăng ký qua decorator `@Controller`. Routes tại `/api/v1/voxels_stream`:

| Method | Path | Mô tả |
|---|---|---|
| POST | `/run` | Bắt đầu xử lý video (chặn đến khi nhấn `q`) |
| GET | `/sessions` | Liệt kê tất cả phiên học |
| GET | `/sessions/stats` | Thống kê tổng hợp |
| GET | `/sessions/daily` | Điểm tập trung hàng ngày (dữ liệu biểu đồ, mặc định 7 ngày) |
| GET | `/sessions/recent` | Phiên học N ngày gần đây |

### VoxelStreamProc (`handlers/VoxelStreamProc.py`)

Vòng lặp xử lý chính. Được decorate với `@Component` (transient DI). Nhận `SessionManager` tùy chọn.

```python
while capture.is_opened():
    frame = capture.read()
    result = detector.detect(frame, capture.timestamp())
    if result.face_landmarks:
        for idx, landmarks in enumerate(result.face_landmarks):
            metrics = extractor.extract(landmarks)
            if result.facial_transformation_matrixes:
                pitch, yaw, roll = head_pose_estimator.estimate(tf_matrix)
                metrics.pitch, metrics.yaw, metrics.roll = pitch, yaw, roll
            state = fsm.update(metrics)
            frame = renderer.render(frame, landmarks, state, metrics)
            if session_manager: session_manager.update(state)
    else:
        state = fsm.update(None)
        frame = renderer.render_no_face(frame, state)
        if session_manager: session_manager.update(state)
    cv2.imshow("Focus Analysis", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"): break
capture.release()
```

### OCVCapture (`services/OCVCapture.py`)

Triển khai `FrameSource`. Mở webcam qua `cv2.VideoCapture(0)` ở 1280×720, lật khung hình ngang (mirror), và cung cấp timestamp đơn điệu tính bằng mili giây qua `time.monotonic()`.

### Detector (`services/Detector.py`)

Context manager bao bọc MediaPipe `FaceLandmarker` ở chế độ **VIDEO**. Tải model từ `config/face_landmarker.task`. Phương thức `detect()` chuyển BGR→RGB, bọc trong `mp.Image`, gọi `detect_for_video()`.

Trả về `FaceLandmarkerResult` với:
- `face_landmarks` — danh sách 478 landmark chuẩn hóa cho mỗi khuôn mặt phát hiện được
- `facial_transformation_matrixes` — danh sách ma trận biến đổi 4×4

### Extractor (`services/Extractor.py`)

Trích xuất các chỉ số khuôn mặt từ lưới 478 điểm MediaPipe:

- **EAR** (Eye Aspect Ratio) – đo độ mở mắt (xem [công thức EAR](#ear-eye-aspect-ratio))
- **MAR** (Mouth Aspect Ratio) – đo độ mở miệng (xem [công thức MAR](#mar-mouth-aspect-ratio))

Các chỉ số landmark sử dụng:

| Metric | Các chỉ số Landmark |
|---|---|
| EAR trái | `33, 160, 158, 133, 153, 144` |
| EAR phải | `362, 385, 387, 263, 373, 380` |
| MAR | `13, 14, 78, 308` |

### HeadPoseEstimator (`services/HeadPoseEstimator.py`)

Trích xuất góc Euler từ ma trận xoay 3×3 của ma trận biến đổi khuôn mặt 4×4 MediaPipe (xem [công thức Head Pose](#head-pose--góc-euler-từ-ma-trận-xoay)). Trả về `(pitch, yaw, roll)` tính bằng độ.

### FaceMetrics (`services/Metrics.py`)

```python
@dataclass
class FaceMetrics:
    left_ear: float
    right_ear: float
    mar: float
    pitch: float | None = None   # được đặt bởi HeadPoseEstimator
    yaw: float | None = None
    roll: float | None = None
    @property
    def ear(self) -> float: return (self.left_ear + self.right_ear) / 2
```

### FaceState (`services/FaceState.py`)

```python
class FaceState(Enum):
    NORMAL        = "NORMAL"
    EYES_CLOSED   = "EYES CLOSED"
    YAWNING       = "YAWNING"
    LOOKING_LEFT  = "LOOKING LEFT"
    LOOKING_RIGHT = "LOOKING RIGHT"
    LOOKING_DOWN  = "LOOKING DOWN"
    ABSENT        = "ABSENT"
```

### ExpressionFSM (`services/ExpressionFSM.py`)

FSM dựa trên hysteresis với `REQUIRED_FRAMES = 4` debouncing.

| Ngưỡng | Giá trị | Hiệu ứng |
|---|---|---|
| `EYE_CLOSE_THRESHOLD` | `0.20` | EAR dưới → `EYES_CLOSED` |
| `MOUTH_OPEN_THRESHOLD` | `0.5` | MAR trên → `YAWNING` |
| `LOOKING_LEFT_THRESHOLD` | `-25.0°` | yaw dưới → `LOOKING_LEFT` |
| `LOOKING_RIGHT_THRESHOLD` | `25.0°` | yaw trên → `LOOKING_RIGHT` |
| `LOOKING_DOWN_THRESHOLD` | `-20.0°` | pitch dưới → `LOOKING_DOWN` |
| `ABSENT_FRAMES` | `90` | không có mặt ~3s → `ABSENT` |

Khi `yaw` vượt quá ±25°, việc kiểm tra ngáp/nhắm mắt bị bỏ qua (quay đầu được ưu tiên).

### FocusAnalyzer (`services/FocusAnalyzer.py`)

Theo dõi điểm tập trung và số đếm sự kiện (xem [công thức Focus Score](#focus-score) và [công thức Focus Level](#focus-level)). Được reset khi `SessionManager.start()`.

| Phương thức | Hành vi |
|---|---|
| `update(state)` | Tăng `total_frames`, `focusing_frames` nếu state nằm trong tập focusing |
| `_on_transition(state)` | Đếm sự kiện khi thay đổi trạng thái |
| `get_summary()` | Trả về dict với tất cả bộ đếm + `focus_score` |
| `derive_focus_level(state)` | Static: `FOCUSING` / `DROWSY` / `LOST_FOCUS` |

### Renderer (`services/Renderer.py`)

Chú thích khung hình với lớp phủ tùy chọn (tất cả **tắt mặc định**):

| Lớp phủ | Flag | Mô tả |
|---|---|---|
| Landmarks | `show_landmarks` | Chấm xanh trên tất cả 478 điểm |
| Bounding box | `show_bbox` | Hình chữ nhật vàng quanh khuôn mặt |
| Text trạng thái/metrics | `show_overlay` | STATE, EAR, MAR, Pitch, Yaw, Roll |
| Không có mặt | `show_overlay` | Thông báo "NO FACE DETECTED" |

### StudySession (`models/StudySession.py`)

```python
@dataclass
class StudySession:
    id: int | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    duration: int = 0                      # giây
    focus_score: float = 100.0
    distraction_count: int = 0
    yawn_count: int = 0
    eye_close_count: int = 0
    looking_left_count: int = 0
    looking_right_count: int = 0
    looking_down_count: int = 0
    absent_count: int = 0
```

## API Endpoints

```bash
# Bắt đầu xử lý video (chặn đến khi nhấn 'q')
curl -X POST http://localhost:8000/api/v1/voxels_stream/run

# Liệt kê tất cả phiên học
curl http://localhost:8000/api/v1/voxels_stream/sessions

# Lấy thống kê tổng hợp
curl http://localhost:8000/api/v1/voxels_stream/sessions/stats

# Lấy điểm hàng ngày (7 ngày gần nhất)
curl "http://localhost:8000/api/v1/voxels_stream/sessions/daily?days=7"

# Lấy phiên gần đây (7 ngày gần nhất)
curl "http://localhost:8000/api/v1/voxels_stream/sessions/recent?days=7"
```

## Phụ thuộc SharedKernel

| Class | Vị trí | Vai trò |
|---|---|---|
| `Container` | `src/SharedKernel/base/Container.py` | DI container |
| `@Component` | `src/SharedKernel/base/Decorators.py` | Đăng ký transient |
| `@Controller` | `src/SharedKernel/base/Decorators.py` | Tự động phát hiện |
| `APIResponse` | `src/SharedKernel/base/APIResponse.py` | Bọc phản hồi |
| `SessionManager` | `src/SharedKernel/persistence/SessionManager.py` | Vòng đời phiên học |
| `StudySessionRepo` | `src/SharedKernel/persistence/StudySessionRepo.py` | Lưu trữ SQLite |
| `CrudORM` | `src/SharedKernel/persistence/CrudORM.py` | ORM SQLite tổng quát |

## Thư viện phụ thuộc

- `mediapipe` — Mô hình Face Landmarker & suy luận
- `opencv-python` — Chụp camera, xử lý ảnh, hiển thị
- `numpy` — Tính toán ma trận cho ước tính head pose
- `fastapi` — HTTP API
- `granian` — ASGI server
