# Kế hoạch: Phân biệt chớp mắt (blink) với nhắm mắt thật

## Vấn đề

Hệ thống hiện tại không phân biệt được **chớp mắt tự nhiên** (blink) và **nhắm mắt kéo dài**. Cả hai đều kích hoạt state `EYES_CLOSED`, dẫn đến:

1. `eye_close_count` tăng lên mỗi lần chớp mắt
2. `distraction_count` tăng — ảnh hưởng sai điểm số tập trung
3. User bị đánh giá là `DROWSY` dù chỉ chớp mắt bình thường

**Mô phỏng:** Một blink thường kéo dài 100-400ms (3-12 frame ở 30 FPS). Với `REQUIRED_FRAMES = 4` (~133ms), hầu hết blink đều đủ dài để vượt qua debounce → trigger `EYES_CLOSED`.

---

## Root Cause

### 1. ExpressionFSM thiếu temporal analysis

`ExpressionFSM._determine_target_state()` chỉ xét từng frame riêng lẻ:

```python
if not is_turning and metrics.ear < self.EYE_CLOSE_THRESHOLD:
    return FaceState.EYES_CLOSED   # ← không biết đây là blink hay nhắm thật
```

Debounce hiện tại (`REQUIRED_FRAMES = 4`) chỉ lọc nhiễu ngắn (<4 frames), không đủ để phân biệt blink (có thể 5-12 frames) với nhắm thật (hàng chục frame).

### 2. FocusAnalyzer đếm mọi transition đến EYES_CLOSED

```python
def _on_transition(self, state: FaceState):
    if state == FaceState.EYES_CLOSED:
        self.eye_close_count += 1
        self.distraction_count += 1
```

Không có cơ chế nào để đánh dấu "transition này là do blink, đừng đếm".

---

## Giải pháp

### 1. Thêm blink detection vào ExpressionFSM

Dùng **counter riêng cho eyes-closed duration** để phân biệt blink (~100-500ms) và nhắm thật (>500ms):

```python
class ExpressionFSM:
    EYE_CLOSE_THRESHOLD = 0.20
    BLINK_MAX_FRAMES = 15        # ~500ms ở 30 FPS — ngưỡng blink tối đa
    REQUIRED_FRAMES = 4          # debounce tối thiểu (giữ nguyên)

    def __init__(self):
        self.state = FaceState.NORMAL
        self.counter = 0
        self.absent_counter = 0
        self._eyes_closed_counter = 0   # mới: đếm số frame liên tiếp EAR < threshold

    def _process_face(self, metrics):
        target_state = self._determine_target_state(metrics)
        self.absent_counter = 0

        # Nếu target là EYES_CLOSED, đếm duration
        if target_state == FaceState.EYES_CLOSED:
            self._eyes_closed_counter += 1
        else:
            self._eyes_closed_counter = 0

        # Nếu đang trong EYES_CLOSED nhưng target != EYES_CLOSED
        # (mắt vừa mở lại) và duration ≤ BLINK_MAX_FRAMES → đó là blink
        if (self.state == FaceState.EYES_CLOSED
                and target_state != FaceState.EYES_CLOSED
                and self._eyes_closed_counter <= self.BLINK_MAX_FRAMES):
            # Đây là blink! Không chuyển state, không đếm distraction
            self.state = FaceState.NORMAL
            self.counter = 0
            self._eyes_closed_counter = 0
            return self.state

        # Debounce giống hiện tại
        if target_state == self.state:
            self.counter = 0
            return self.state

        self.counter += 1
        if self.counter >= self.REQUIRED_FRAMES:
            self.state = target_state
            self.counter = 0
        return self.state
```

**Giải thích luồng blink:**

```
Frame   EAR     target          state         _eyes_closed_counter
  t     0.25    NORMAL          NORMAL         0
  t+1   0.15    EYES_CLOSED     NORMAL         1
  t+2   0.12    EYES_CLOSED     NORMAL         2
  t+3   0.11    EYES_CLOSED     NORMAL         3
  t+4   0.10    EYES_CLOSED     NORMAL         4    ← counter >= REQUIRED_FRAMES
                                                      → state = EYES_CLOSED
                                                         eye_close_count++ (hmm)
  ...
  t+8   0.25    NORMAL          EYES_CLOSED    8    ← mắt vừa mở
                                                      _eyes_closed_counter = 8 ≤ 15
                                                      → ĐÂY LÀ BLINK
                                                      → state = NORMAL (hoàn nguyên)
```

**Vấn đề:** Transition đến `EYES_CLOSED` vẫn xảy ra tại frame t+4 (vì `_eyes_closed_counter` chưa vượt `BLINK_MAX_FRAMES` nhưng REQUIRED_FRAMES đã đạt). Cần tinh chỉnh — không cho phép state chuyển sang EYES_CLOSED nếu `_eyes_closed_counter` còn ≤ `BLINK_MAX_FRAMES`.

### 2. Sửa logic — không transition đến EYES_CLOSED khi đang ở blink range

Giải pháp chính xác hơn: **trì hoãn transition đến EYES_CLOSED cho đến khi vượt BLINK_MAX_FRAMES**.

```python
def _process_face(self, metrics):
    target_state = self._determine_target_state(metrics)
    self.absent_counter = 0

    # Đếm số frame EAR dưới threshold
    if target_state == FaceState.EYES_CLOSED:
        self._eyes_closed_counter += 1
    else:
        self._eyes_closed_counter = 0

    # Nếu mắt đang nhắm nhưng chưa đủ lâu để coi là "nhắm thật"
    # → force target về NORMAL để debounce không kích hoạt EYES_CLOSED
    if (target_state == FaceState.EYES_CLOSED
            and self._eyes_closed_counter <= self.BLINK_MAX_FRAMES):
        target_state = FaceState.NORMAL

    # Debounce giống hiện tại
    if target_state == self.state:
        self.counter = 0
        return self.state

    self.counter += 1
    if self.counter >= self.REQUIRED_FRAMES:
        self.state = target_state
        self.counter = 0
    return self.state
```

**Kết quả:**
- Blink (<15 frame): `_eyes_closed_counter` reset về 0 trước khi kịp vượt 15 → `target_state` luôn bị force về NORMAL → không bao giờ vào `EYES_CLOSED`
- Nhắm thật (≥15 frame): `_eyes_closed_counter` vượt 15 → force không còn hiệu lực → `target_state` là `EYES_CLOSED` → debounce 4 frame → state = `EYES_CLOSED`

### 3. Reset trạng thái trong `reset()`

```python
def reset(self):
    self.state = FaceState.NORMAL
    self.counter = 0
    self.absent_counter = 0
    self._eyes_closed_counter = 0
```

### 4. FocusAnalyzer — blink counter riêng (optional)

Thêm blink counter để monitoring, không ảnh hưởng distraction:

```python
class FocusAnalyzer:
    def __init__(self):
        self.reset()

    def reset(self):
        # ... giữ nguyên ...
        self.blink_count = 0        # mới

    def _on_transition(self, state: FaceState):
        # ... giữ nguyên ...
        # Không cần xử lý blink ở đây vì blink không tạo transition
```

Vì `EYES_CLOSED` không còn được trigger bởi blink, `FocusAnalyzer` không cần thay đổi logic đếm. Tuy nhiên, có thể thêm `blink_count` riêng nếu cần theo dõi.

### 5. Config — thêm `BLINK_MAX_FRAMES`

Cho phép user tinh chỉnh:

```yaml
# config.yaml
tracking:
  ear_threshold: 0.2
  blink_max_frames: 15      # mới: blink tối đa ~500ms
  required_frames: 4
```

```python
# config.py
BLINK_MAX_FRAMES = _cfg.tracking.blink_max_frames
```

```python
# dashboard.py __init__
self.fsm.BLINK_MAX_FRAMES = BLINK_MAX_FRAMES
```

### 6. TrackingSettingsDialog — cho phép chỉnh blink threshold

Thêm spinbox hoặc slider để user tùy chỉnh `blink_max_frames` (phạm vi 5-60, step 5).

---

## Tóm tắt thay đổi

| # | Task | Files | Độ phức tạp |
|---|------|-------|------------|
| 1 | Thêm `_eyes_closed_counter`, sửa `_process_face` | `services/ExpressionFSM.py` | Thấp — ~15 dòng |
| 2 | Reset counter trong `reset()` | `services/ExpressionFSM.py` | Thấp — 1 dòng |
| 3 | Giữ nguyên `FocusAnalyzer` | — | Không đổi |
| 4 | Thêm `BLINK_MAX_FRAMES` vào config | `config.yaml`, `config.py` | Thấp |
| 5 | Gán `self.fsm.BLINK_MAX_FRAMES` trong dashboard | `ui/dashboard.py` | Thấp — 1 dòng |
| 6 | (Optional) Thêm UI settings cho blink threshold | `ui/tracking_settings.py` | Trung bình |

## Luồng dữ liệu mới

```
metrics.ear < EAR_THRESHOLD?
    │
    ├── Có → _eyes_closed_counter++
    │        │
    │        ├── counter ≤ BLINK_MAX_FRAMES → force target = NORMAL
    │        │                                  ↓ blink bị bỏ qua
    │        └── counter > BLINK_MAX_FRAMES → target = EYES_CLOSED
    │                                           ↓ nhắm thật
    │
    └── Không → _eyes_closed_counter = 0
                 target = NORMAL
```

## Rủi ro

| Rủi ro | Mức độ | Giảm thiểu |
|--------|--------|------------|
| User nhắm mắt cố ý ngắn (<500ms) vẫn bị bỏ qua | Trung bình | `BLINK_MAX_FRAMES` có thể config — user tự điều chỉnh nếu muốn nhạy hơn |
| False positive — mắt híp (EAR gần threshold) lâu nhưng không nhắm hẳn | Thấp | `EAR_THRESHOLD = 0.20` thấp, mắt híp thường >0.20 |
