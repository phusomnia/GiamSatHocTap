# Kế hoạch: Nút Stop GUI + Chỉ track 1 khuôn mặt

## 1. Chỉ track 1 khuôn mặt

### Vấn đề
Cả `dashboard.py` và `VoxelStreamProc.py` đều dùng vòng lặp `for idx, landmarks in enumerate(result.face_landmarks)` — xử lý tất cả khuôn mặt phát hiện được, gây dư thừa tài nguyên.

### Giải pháp
Chỉ xử lý khuôn mặt đầu tiên (`face_landmarks[0]`), bỏ qua vòng lặp.

### File cần sửa

| File | Dòng | Sửa |
|------|------|-----|
| `frontend/native/ui/dashboard.py` | 423 | `for idx, landmarks in enumerate(result.face_landmarks):` → `landmarks = result.face_landmarks[0]` + `idx = 0` cố định cho tf_matrix |
| `src/Features/VoxelStream_Module/handlers/VoxelStreamProc.py` | 67 | Tương tự — xử lý `face_landmarks[0]` duy nhất |

> Ghi chú: `Detector.__init__` đã có `num_faces=1` mặc định, nhưng MediaPipe vẫn có thể trả về >1 face. Cần hardcode ở logic xử lý.

---

## 2. Nút Stop trên GUI

### Vấn đề
GUI có nút Stop (`dashboard.py:249`) gọi `_stop_session()`, chỉ dừng `QTimer` nhưng không dừng được nếu `_process_frame` đang xử lý nặng. Không có cơ chế thoát tức thì.

### Giải pháp
Thêm **stop flag** (`_stop_requested`) được kiểm tra đầu mỗi frame.

### File cần sửa: `frontend/native/ui/dashboard.py`

#### a) Thêm flag trong `__init__`
```python
self._stop_requested = False
```

#### b) Đầu `_process_frame` kiểm tra flag
```python
def _process_frame(self) -> None:
    if self._stop_requested:
        self._stop_session()
        return
    if not self._is_running:
        return
    # ... xử lý frame
```

#### c) `_stop_session` set flag trước khi dừng timer
```python
def _stop_session(self) -> None:
    self._stop_requested = True
    self._timer.stop()
    self._is_running = False
    self.start_btn.setEnabled(True)
    self.stop_btn.setEnabled(False)
    session = self.session_manager.stop()
    if session:
        QMessageBox.information(self, "Session", f"Focus Score: {session.focus_score:.1f}%")
    self._clear_cards()
    self.is_registered = False
    self.auth_fail_count = 0
    self.auth_warning = False
    if hasattr(self, 'face_auth'):
        self.face_auth.registered_embedding = None
```

#### d) Reset flag khi start session mới
```python
def _start_session(self) -> None:
    if self._is_running:
        return
    self._stop_requested = False
    # ... rest
```

---

## 3. Dừng VoxelStreamProc (cho FastAPI endpoint)

### Vấn đề
`VoxelStreamProc.run_tracker()` chạy blocking loop (`while self.capture.is_opened()`), chỉ thoát được bằng phím `q`. Không có API `/stop` để dừng từ xa.

### Giải pháp
Thêm stop flag + method `stop()` + endpoint `/stop` + threading cho `/run`.

### File: `src/Features/VoxelStream_Module/handlers/VoxelStreamProc.py`

```python
class VoxelStreamProc:
    def __init__(self):
        # ... existing
        self._stop_requested = False

    def stop(self):
        self._stop_requested = True

    def run_tracker(self, session_manager=None):
        self._stop_requested = False
        # ... existing init code
        with Detector() as detector:
            while self.capture.is_opened():
                if self._stop_requested:
                    break
                # ... existing frame processing
        self.capture.release()
        if session_manager:
            session_manager.stop()
```

### File: `src/Features/VoxelStream_Module/controllers/VoxelStreamController.py`

Thêm endpoint `/stop`:

```python
@self.router.post("/stop", description="Stop voxel stream processing")
def stop_voxel_stream():
    self.voxel_stream_proc.stop()
    return APIResponse(status_code=200, message="Stop requested")
```

Sửa endpoint `/run` chạy background thread:

```python
import threading

@self.router.post("/run", description="Start voxel stream processing")
def run_voxel_stream():
    session_manager = SessionManager(StudySessionRepo())
    session_manager.start()
    thread = threading.Thread(
        target=self.voxel_stream_proc.run_tracker,
        args=(session_manager,),
        daemon=True
    )
    thread.start()
    return APIResponse(
        status_code=200,
        message="Voxel stream processing started"
    )
```

> Lưu ý: `session_manager.stop()` được chuyển vào cuối `run_tracker()` thay vì gọi sau `thread.start()`.

---

## 4. Nút Pause trên GUI

### Vấn đề
Hiện chỉ có Start/Stop. Stop kết thúc hẳn phiên học (lưu DB, reset state). Không có cơ chế tạm dừng để người dùng rời khỏi bàn tạm thời mà không kết thúc phiên.

### Giải pháp
Thêm nút Pause/Resume toggle:
- **Pause:** Đóng băng khung hình hiện tại, dừng xử lý frame, tạm dừng đồng hồ session. Không lưu DB.
- **Resume:** Tiếp tục xử lý frame, đồng hồ chạy lại. Session vẫn là phiên cũ.

### File cần sửa: `frontend/native/ui/dashboard.py`

#### a) Thêm trạng thái `_is_paused` trong `__init__`
```python
self._is_paused = False
self._paused_frame: np.ndarray | None = None  # frame đóng băng
```

#### b) Thêm nút Pause trong `_build_monitor_page` (cạnh Start/Stop)
```python
self.pause_btn = self._button("Pause", WARNING)
self.pause_btn.clicked.connect(self._toggle_pause)
self.pause_btn.setEnabled(False)
controls.addWidget(self.pause_btn)
```

#### c) `_toggle_pause` — chuyển đổi Pause/Resume
```python
def _toggle_pause(self) -> None:
    if not self._is_paused:
        # Pause
        self._is_paused = True
        self._timer.stop()
        self._paused_frame = self.capture.read()  # chụp frame cuối
        self.pause_btn.setText("Resume")
        self.pause_btn.setStyleSheet(...)  # style màu SUCCESS
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)    # vẫn có thể Stop hẳn
    else:
        # Resume
        self._is_paused = False
        self._paused_frame = None
        self.pause_btn.setText("Pause")
        self.pause_btn.setStyleSheet(...)  # style màu WARNING
        self._timer.start()
```

#### d) Kiểm tra `_is_paused` đầu `_process_frame`
```python
def _process_frame(self) -> None:
    if self._stop_requested:
        self._stop_session()
        return
    if self._is_paused:
        return  # giữ nguyên frame, không xử lý
    if not self._is_running:
        return
```

#### e) Hiển thị frame đóng băng khi paused
Trong `_process_frame`, nếu `_is_paused` và `_paused_frame` không None, vẫn render frame đó + overlay "PAUSED".

Hoặc đơn giản hơn: không cần vẽ lại, Qt giữ pixmap cũ.

#### f) Cập nhật `_start_session` — bật Pause khi session bắt đầu
```python
def _start_session(self) -> None:
    # ...
    self.pause_btn.setEnabled(True)
```

#### g) Cập nhật `_stop_session` — tắt hết về mặc định
```python
def _stop_session(self) -> None:
    # ...
    self._is_paused = False
    self._paused_frame = None
    self.pause_btn.setText("Pause")
    self.pause_btn.setEnabled(False)
```

#### h) Thêm overlay "PAUSED" khi đang pause
Trong `_render_frame`, chèn chữ "PAUSED" nếu `_is_paused`:
```python
if self._is_paused:
    cv2.putText(frame, "PAUSED", (frame.shape[1]//2 - 80, frame.shape[0]//2),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
```

### Trạng thái các nút theo từng phase

| Phase | Start | Pause | Stop |
|-------|-------|-------|------|
| Idle (chưa start) | Enabled | Disabled | Disabled |
| Running | Disabled | **Enabled ("Pause")** | Enabled |
| Paused | Disabled | **Enabled ("Resume")** | Enabled |
| Stopped | Enabled | Disabled | Disabled |

### Lưu ý
- Pause không ảnh hưởng đến `SessionManager` — không gọi `stop()`, không reset analyzer.
- Khi Resume, `_is_paused = False` và timer được start lại → `_process_frame` tiếp tục chạy.
- Khi Stop ở trạng thái Paused → session kết thúc bình thường (lưu DB).

---

## Tóm tắt thứ tự triển khai

| # | Task | Files | Độ phức tạp |
|---|------|-------|------------|
| 1 | Track 1 face (GUI) | `dashboard.py` | Thấp — 2 dòng |
| 2 | Track 1 face (Handler) | `VoxelStreamProc.py` | Thấp — 2 dòng |
| 3 | Stop flag GUI | `dashboard.py` | Thấp — flag + check |
| 4 | Pause/Resume GUI | `dashboard.py` | Trung bình — button + state machine |
| 5 | Stop flag cho FastAPI | `VoxelStreamProc.py`, `VoxelStreamController.py` | Trung bình — stop flag + `/stop` + threading |
