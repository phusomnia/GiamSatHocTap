# Kế hoạch: Fix giật/lag khung hình khi xác thực và track

## Vấn đề

Camera bị giật khung hình (stutter) ở 2 thời điểm:

1. **Khi đăng ký khuôn mặt** — `FaceAuthenticator.register_face()` gọi `DeepFace.represent()` với `detector_backend='mtcnn'` mỗi 15 frames, block main thread 1-3s
2. **Khi xác thực định kỳ** — `FaceAuthenticator.verify_face()` cũng gọi `DeepFace.represent()` mỗi 90 frames, block 1-3s giống đăng ký

Cả hai đều chạy **synchronous trên QTimer callback** (`_process_frame`), trong khi timer interval chỉ 33ms (~30 FPS). Một lần block 1-3s đồng nghĩa với **30-90 frame bị nhảy cóc**.

---

## Root Cause

`FaceAuth.py:14-18`:
```python
embedding_objs = DeepFace.represent(
    img_path=frame,
    model_name=self.model_name,
    enforce_detection=True,
    detector_backend='mtcnn'   # ← MTCNN rất chậm (1-3s)
)
```

| Backend | Ưu điểm | Nhược điểm |
|---------|---------|------------|
| `mtcnn` | Chính xác cao, bắt được mặt nghiêng | Rất chậm (1-3s) |
| `opencv` | Nhanh (~200ms) | Kém chính xác, dễ false negative |
| `ssd` | Cân bằng (~500ms) | Yêu cầu tensorflow |
| `retinaface` | Chính xác nhất | Rất chậm (>2s) |

Toàn bộ pipeline `_process_frame` (dashboard.py:411) chạy trên main thread Qt, không có bất kỳ threading nào → bất kỳ blocking call nào cũng làm treo toàn bộ UI và camera.

---

## Giải pháp

### 1. Tách DeepFace ra thread riêng (Background Verification Thread)

Tạo một thread liên tục chạy verify ở background; main thread chỉ đọc kết quả mới nhất từ shared variable.

#### 1a. Thêm `BackgroundVerifier` class trong `FaceAuth.py`

```python
import threading
import time
import numpy as np
from collections import deque

class BackgroundVerifier:
    """Chạy DeepFace verify trong thread riêng, không block main thread."""

    def __init__(self, face_auth: FaceAuthenticator, interval_frames=90, fps=30):
        self.face_auth = face_auth
        self.interval = interval_frames / fps  # 90/30 = 3 giây
        self._latest_frame: np.ndarray | None = None
        self._result = True          # mặc định: hợp lệ
        self._running = False
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()

    def submit_frame(self, frame: np.ndarray):
        """Main thread gửi frame mới nhất để verifier xử lý."""
        with self._lock:
            self._latest_frame = frame.copy()

    @property
    def is_verified(self) -> bool:
        """Main thread đọc kết quả verify mới nhất (không block)."""
        with self._lock:
            return self._result

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def _run(self):
        while self._running:
            time.sleep(self.interval)
            with self._lock:
                frame = self._latest_frame
            if frame is None:
                continue
            try:
                ok = self.face_auth.verify_face(frame)
            except Exception:
                ok = False
            with self._lock:
                self._result = ok
```

#### 1b. Sửa `dashboard.py` — dùng `BackgroundVerifier`

```python
# Trong __init__:
self.background_verifier = BackgroundVerifier(self.face_auth)

# Trong _start_session:
self.background_verifier.start()

# Trong _process_frame — bỏ verify_face trực tiếp, chỉ submit frame:
if self.auth_frame_count % 90 == 0:
    self.background_verifier.submit_frame(frame)

# Đọc kết quả verify mỗi frame (không block):
is_correct_user = self.background_verifier.is_verified
if not is_correct_user and self.auth_frame_count % 90 == 0:
    self.auth_warning = True
    self.auth_fail_count += 1
    print(f"⚠️ Phát hiện sai người lần {self.auth_fail_count}!")
elif is_correct_user and self.auth_frame_count % 90 == 0:
    self.auth_warning = False
    self.auth_fail_count = 0

# Trong _stop_session:
self.background_verifier.stop()
```

---

### 2. Đăng ký khuôn mặt — chỉ gọi 1 lần + debounce

#### 2a. Giảm tần suất từ 15 frames → 30 frames
```python
# dashboard.py — thay:
if self.register_attempt_count % 15 == 0:
# thành:
if self.register_attempt_count % 30 == 0:
```

#### 2b. Tối ưu `register_face` — chạy trong thread ngắn
Dùng `threading.Thread` + callback:

```python
def _try_register_face(self, frame):
    def _register():
        success = self.face_auth.register_face(frame)
        if success:
            self.is_registered = True
            print("✅ Đăng ký khuôn mặt thành công!")
    threading.Thread(target=_register, daemon=True).start()
```

Và trong loop chỉ check `self.is_registered` (không gọi register trực tiếp).

---

### 3. Tối ưu Detector backend (tùy chọn)

Hiện tại dùng MTCNN (`detector_backend='mtcnn'`). Có thể đổi sang `'ssd'` để giảm thời gian xử lý:

```python
# FaceAuth.py line 17:
detector_backend='ssd'  # thay vì 'mtcnn'
```

Nhưng SSD yêu cầu tensorflow đã load sẵn. Cần cân nhắc giữa tốc độ và độ chính xác.

Nếu muốn giữ MTCNN thì giải pháp thread (mục 1) là đủ — vì thread không block main loop.

---

### 4. MediaPipe tracking — kiểm tra FPS thực tế

`FRAME_INTERVAL_MS = 33` (~30 FPS). MediaPipe `detect_for_video` có thể chậm nếu CPU yếu.

**Giải pháp dự phòng:** Config cho phép giảm FPS:

```yaml
# config.yaml
camera:
  frame_interval_ms: 50   # giảm từ 33 → 20 FPS
```

Hoặc dynamic FPS: bỏ qua frame nếu `_process_frame` phát hiện đang lag:

```python
# Dashboard.__init__:
self._skip_next = False

# _process_frame:
if self._skip_next:
    self._skip_next = False
    return  # bỏ qua 1 frame để catch up
self._skip_next = True  # chỉ xử lý mỗi 2 frame
```

---

## Tóm tắt thay đổi

| # | Task | Files | Độ phức tạp |
|---|------|-------|------------|
| 1 | Thêm `BackgroundVerifier` class | `services/FaceAuth.py` | Trung bình — thread + shared state |
| 2 | Tích hợp `BackgroundVerifier` vào dashboard | `ui/dashboard.py` | Trung bình — start/stop/submit/read |
| 3 | Tối ưu register_face — chạy thread ngắn | `ui/dashboard.py` | Thấp — threading + callback |
| 4 | (Tùy chọn) Giảm tần suất register 15→30 | `ui/dashboard.py` | Thấp — 1 dòng |
| 5 | (Tùy chọn) Dynamic FPS skip frame | `ui/dashboard.py` | Thấp — flag skip |

## Luồng dữ liệu mới

```
Main Thread (QTimer)                        Background Thread
─────────────────────                       ─────────────────
MediaPipe detect → extract → fsm → render
       │
       └── mỗi 90 frame: submit_frame() ──→ BackgroundVerifier._run()
                                                   │
                                              DeepFace.represent()
                                                   │
                                              cập nhật _result
       ←── mỗi frame: đọc is_verified ──────
       │
       if not verified → auth_warning
```

Main thread không bao giờ block vì DeepFace. Giật/lag được loại bỏ hoàn toàn.
